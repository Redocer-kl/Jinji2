import unittest
from models.author import Author
from models.user import User
from models.currency import Currency
from models.user_currency import UserCurrency


class TestModels(unittest.TestCase):

    def test_author(self):
        a = Author("Ivan", "G1")
        self.assertEqual(a.name, "Ivan")
        self.assertEqual(a.group, "G1")
        with self.assertRaises(TypeError):
            a.name = 123

    def test_user(self):
        u = User(1, "Alice")
        self.assertEqual(u.id, 1)
        self.assertEqual(u.name, "Alice")
        with self.assertRaises(ValueError):
            User(0, "X")

    def test_currency(self):
        c = Currency(id="R00001", num_code="840", char_code="USD", name="Dollar", value=90.0, nominal=1)
        self.assertEqual(c.char_code, "USD")
        with self.assertRaises(TypeError):
            c.value = "not-a-number"

    def test_user_currency(self):
        uc = UserCurrency(1, 1, "R00001")
        self.assertEqual(uc.user_id, 1)
        self.assertEqual(uc.currency_id, "R00001")


if __name__ == '__main__':
    unittest.main()
