"""Основной файл: HTTP server, routing и запуск Jinja2.

- Инициализация SQLite БД и таблиц (users, currency, user_currency, meta, currency_history).
- CRUD: список пользователей, просмотр пользователя, список валют, удаление валюты.
- Подписки пользователей на валюты (subscribe/unsubscribe).
- Исторические записи курсов валют (currency_history) при обновлении курсов.
- Endpoint для получения исторических данных в JSON (/currency/history).
- На странице пользователя отображается график динамики (Chart.js) для каждой подписки.

Запуск:
    python myapp.py

URL-эндпойнты:
    /              - index
    /author        - author info
    /users         - list users
    /user?id=<id>  - user details (показывает подписки и графики)
    /currencies    - list currencies (с кнопкой "Обновить")
    /currency/delete?id=<id> - удалить валюту по id
    /subscribe?user_id=...&currency_id=... - добавить подписку (GET для демо)
    /unsubscribe?uc_id=... - удалить подписку по id
    /currency/history?id=...&months=3 - вернуть JSON исторических данных
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from jinja2 import Environment, PackageLoader, select_autoescape
from typing import Dict, Any, List, Optional, Tuple
import json
import os
import sqlite3
import datetime

from models import Author, App
from models.user import User
from models.currency import Currency
from utils.currencies_api import get_currencies

BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, 'data', 'app.db')


os.makedirs(os.path.join(BASE_DIR, 'data'), exist_ok=True)


env = Environment(
    loader=PackageLoader("myapp"),
    autoescape=select_autoescape(["html", "xml"]),
)


template_index = env.get_template("index.html")
template_users = env.get_template("users.html")
template_user = env.get_template("user.html")
template_currencies = env.get_template("currencies.html")
template_author = env.get_template("author.html")


main_author = Author(name="Пак Александра Артемовна", group="Р3122")
app_meta = App(name="CurrenciesListApp", version="0.1", author=main_author)


class DB:
    """
    Класс для работы с бд
    Создание таблиц и все необходимые запросы
    """

    def __init__(self, path: str) -> None:
        self.path = path
        self._ensure_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_schema(self) -> None:
        """Создание таблиц в бд"""
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS currency (
                    id TEXT PRIMARY KEY,
                    num_code TEXT,
                    char_code TEXT,
                    name TEXT,
                    value REAL,
                    nominal INTEGER,
                    updated_at TEXT
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS user_currency (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    currency_id TEXT NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES users(id),
                    FOREIGN KEY(currency_id) REFERENCES currency(id)
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS currency_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    currency_id TEXT NOT NULL,
                    value REAL,
                    nominal INTEGER,
                    recorded_at TEXT
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS meta (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
                """
            )
            conn.commit()

    def list_users(self) -> List[Dict[str, Any]]:
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, name FROM users ORDER BY id")
            return [dict(row) for row in cur.fetchall()]

    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, name FROM users WHERE id = ?", (user_id,))
            row = cur.fetchone()
            return dict(row) if row else None

    def add_user(self, user_id: int, name: str) -> None:
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("INSERT OR REPLACE INTO users (id, name) VALUES (?,?)", (user_id, name))
            conn.commit()

    def list_currencies(self) -> List[Dict[str, Any]]:
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM currency ORDER BY char_code")
            return [dict(row) for row in cur.fetchall()]

    def get_currency(self, cid: str) -> Optional[Dict[str, Any]]:
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM currency WHERE id = ?", (cid,))
            row = cur.fetchone()
            return dict(row) if row else None

    def upsert_currency(self, data: Dict[str, Any]) -> None:
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO currency (id, num_code, char_code, name, value, nominal, updated_at)
                VALUES (:id, :num_code, :char_code, :name, :value, :nominal, :updated_at)
                ON CONFLICT(id) DO UPDATE SET
                    num_code=excluded.num_code,
                    char_code=excluded.char_code,
                    name=excluded.name,
                    value=excluded.value,
                    nominal=excluded.nominal,
                    updated_at=excluded.updated_at
                """,
                data,
            )
            conn.commit()
            self.add_currency_history(data['id'], data['value'], data.get('nominal', 1), data.get('updated_at'))

    def delete_currency(self, cid: str) -> None:
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM currency WHERE id = ?", (cid,))
            conn.commit()

    def list_user_subscriptions(self, user_id: int) -> List[Dict[str, Any]]:
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT uc.id as uc_id, c.* FROM user_currency uc
                JOIN currency c ON c.id = uc.currency_id
                WHERE uc.user_id = ?
                """,
                (user_id,),
            )
            return [dict(row) for row in cur.fetchall()]

    def add_subscription(self, user_id: int, currency_id: str) -> None:
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO user_currency (user_id, currency_id) VALUES (?, ?)",
                (user_id, currency_id),
            )
            conn.commit()

    def remove_subscription(self, uc_id: int) -> None:
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM user_currency WHERE id = ?", (uc_id,))
            conn.commit()

    def add_currency_history(self, currency_id: str, value: float, nominal: int, recorded_at: Optional[str]) -> None:
        recorded_at = recorded_at or datetime.datetime.utcnow().isoformat()
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO currency_history (currency_id, value, nominal, recorded_at) VALUES (?, ?, ?, ?)",
                (currency_id, value, nominal, recorded_at),
            )
            conn.commit()

    def get_currency_history(self, currency_id: str, months: int = 3) -> List[Dict[str, Any]]:
        cutoff = datetime.datetime.utcnow() - datetime.timedelta(days=30 * months)
        cutoff_iso = cutoff.isoformat()
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT recorded_at, value, nominal FROM currency_history WHERE currency_id = ? AND recorded_at >= ? ORDER BY recorded_at",
                (currency_id, cutoff_iso),
            )
            return [dict(row) for row in cur.fetchall()]


db = DB(DB_PATH)


class SimpleHandler(BaseHTTPRequestHandler):

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        qs = parse_qs(parsed.query)

        try:
            if path == "/":
                self.handle_index()
            elif path == "/author":
                self.handle_author()
            elif path == "/users":
                self.handle_users()
            elif path == "/user":
                self.handle_user(qs)
            elif path == "/currencies":
                self.handle_currencies(qs)
            elif path == "/currency/delete":
                self.handle_currency_delete(qs)
            elif path == "/subscribe":
                self.handle_subscribe(qs)
            elif path == "/unsubscribe":
                self.handle_unsubscribe(qs)
            elif path == "/currency/history":
                self.handle_currency_history(qs)
            elif path.startswith("/static/"):
                self.handle_static(path)
            else:
                self.send_error(404, "Not Found")
        except Exception as exc:
            self.send_response(500)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(str(exc).encode("utf-8"))

    def handle_index(self) -> None:
        html = template_index.render(myapp=app_meta.name, author=main_author.to_dict())
        self._send_html(html)

    def handle_author(self) -> None:
        html = template_author.render(author=main_author.to_dict(), app=app_meta.to_dict())
        self._send_html(html)

    def handle_users(self) -> None:
        users_data = db.list_users()
        html = template_users.render(users=users_data)
        self._send_html(html)

    def handle_user(self, qs: Dict[str, Any]) -> None:
        id_vals = qs.get("id")
        if not id_vals:
            self.send_error(400, "Missing id parameter")
            return
        try:
            uid = int(id_vals[0])
        except ValueError:
            self.send_error(400, "Invalid id parameter")
            return
        user = db.get_user(uid)
        if not user:
            self.send_error(404, "User not found")
            return
        subs = db.list_user_subscriptions(uid)
        html = template_user.render(user=user, subscriptions=subs)
        self._send_html(html)

    def handle_currencies(self, qs: Dict[str, Any]) -> None:
        do_refresh = False
        refresh = qs.get('refresh')
        if refresh and refresh[0] == '1':
            do_refresh = True
        else:
            if not db.list_currencies():
                do_refresh = True

        if do_refresh:
            try:
                raw = get_currencies()
            except Exception as exc:
                self.send_response(500)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.end_headers()
                self.wfile.write(f"Failed to fetch currencies: {exc}".encode("utf-8"))
                return
            now = datetime.datetime.utcnow().isoformat()
            for r in raw:
                nominal = int(r.get('nominal') or 1)
                try:
                    value = float(r.get('value') or 0.0)
                except Exception:
                    value = 0.0
                db.upsert_currency({
                    'id': r.get('id'),
                    'num_code': r.get('num_code'),
                    'char_code': r.get('char_code'),
                    'name': r.get('name'),
                    'value': value,
                    'nominal': nominal,
                    'updated_at': now,
                })

        currencies = db.list_currencies()
        for c in currencies:
            try:
                c['per_unit'] = float(c['value']) / int(c['nominal'])
            except Exception:
                c['per_unit'] = 0.0
        html = template_currencies.render(currencies=currencies)
        self._send_html(html)

    def handle_currency_delete(self, qs: Dict[str, Any]) -> None:
        id_vals = qs.get('id')
        if not id_vals:
            self.send_error(400, 'Missing id parameter')
            return
        cid = id_vals[0]
        db.delete_currency(cid)
        self.send_response(302)
        self.send_header('Location', '/currencies')
        self.end_headers()

    def handle_subscribe(self, qs: Dict[str, Any]) -> None:
        """Создать подписку пользователя к валюте.

        Параметры: user_id, currency_id
        """
        user_vals = qs.get('user_id')
        cur_vals = qs.get('currency_id')
        if not user_vals or not cur_vals:
            self.send_error(400, 'Missing user_id or currency_id')
            return
        try:
            user_id = int(user_vals[0])
        except ValueError:
            self.send_error(400, 'Invalid user_id')
            return
        currency_id = cur_vals[0]
        if not db.get_user(user_id):
            self.send_error(404, 'User not found')
            return
        if not db.get_currency(currency_id):
            self.send_error(404, 'Currency not found')
            return
        db.add_subscription(user_id, currency_id)
        self.send_response(302)
        self.send_header('Location', f'/user?id={user_id}')
        self.end_headers()

    def handle_unsubscribe(self, qs: Dict[str, Any]) -> None:
        """Убрать подписку по uc_id (user_currency.id)
        Параметры: uc_id
        """
        uc_vals = qs.get('uc_id')
        if not uc_vals:
            self.send_error(400, 'Missing uc_id')
            return
        try:
            uc_id = int(uc_vals[0])
        except ValueError:
            self.send_error(400, 'Invalid uc_id')
            return
        db.remove_subscription(uc_id)
        self.send_response(302)
        self.send_header('Location', '/users')
        self.end_headers()

    def handle_currency_history(self, qs: Dict[str, Any]) -> None:
        """ Возвращает историю валюты как JSON для currency_id. Параметры: id, months (необязателен)"""
        id_vals = qs.get('id')
        months_vals = qs.get('months')
        if not id_vals:
            self.send_error(400, 'Missing id parameter')
            return
        cid = id_vals[0]
        months = 3
        if months_vals:
            try:
                months = int(months_vals[0])
            except ValueError:
                months = 3
        history = db.get_currency_history(cid, months=months)
        out = []
        for h in history:
            try:
                per_unit = float(h['value']) / int(h['nominal'])
            except Exception:
                per_unit = 0.0
            out.append({'recorded_at': h['recorded_at'], 'value': h['value'], 'nominal': h['nominal'], 'per_unit': per_unit})
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps(out).encode('utf-8'))

    def handle_static(self, path: str) -> None:
        rel = path[len("/static/") :]
        fs_path = os.path.join(BASE_DIR, "static", rel)
        if not os.path.isfile(fs_path):
            self.send_error(404, "Static file not found")
            return
        with open(fs_path, "rb") as fh:
            content = fh.read()
        self.send_response(200)
        if fs_path.endswith(".css"):
            self.send_header("Content-Type", "text/css; charset=utf-8")
        else:
            self.send_header("Content-Type", "application/octet-stream")
        self.end_headers()
        self.wfile.write(content)

    def _send_html(self, content: str) -> None:
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(content.encode('utf-8'))


def run(server_port: int = 8000) -> None:
    """Запустить сервер на нужном порте"""
    server = HTTPServer(("", server_port), SimpleHandler)
    print(f"Сервер запущен на http://localhost:{server_port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Сервер закрыт")
        server.server_close()


if __name__ == "__main__":
    run()
