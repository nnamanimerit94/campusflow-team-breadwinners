import unittest

from campusflow.validation import validate_affected_users

class TestAffectedUsersValidation(unittest.TestCase):
    def test_accepts_positive_integer(self):
        result = validate_affected_users(5)
        self.assertEqual(result, 5)

    def test_rejects_zero(self):
        with self.assertRaises(ValueError):
            validate_affected_users(0)

    def test_rejects_nonint(self):
        with self.assertRaises(TypeError):
            validate_affected_users("hello")

    def test_rejects_boolean(self):
        with self.assertRaises(TypeError):
            validate_affected_users(True)

    def test_rejects_negative_integers(self):
        with self.assertRaises(ValueError):
            validate_affected_users(-10)

    def test_rejects_floating_numbers(self):
        with self.assertRaises(TypeError):
            validate_affected_users(5.0)

    def test_accepts_minimum_valid_integer(self):
        result = validate_affected_users(1)
        self.assertEqual(result, 1)