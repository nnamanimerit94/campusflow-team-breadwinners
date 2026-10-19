import unittest

from campusflow.priority import calculate_priority


class TestCalculatePriority(unittest.TestCase):

    def test_critical_priority(self):
        result = calculate_priority("high", 15)
        self.assertEqual(result, "critical")

    def test_high_priority_from_urgency(self):
        result = calculate_priority("high", 2)
        self.assertEqual(result, "high")

    def test_high_priority_from_affected_users(self):
        result = calculate_priority("low", 12)
        self.assertEqual(result, "high")

    def test_medium_priority_from_urgency(self):
        result = calculate_priority("medium", 2)
        self.assertEqual(result, "medium")

    def test_medium_priority_from_affected_users(self):
        result = calculate_priority("low", 5)
        self.assertEqual(result, "medium")

    def test_low_priority(self):
        result = calculate_priority("low", 1)
        self.assertEqual(result, "low")

    def test_accepts_uppercase_urgency(self):
        result = calculate_priority("HIGH", 10)
        self.assertEqual(result, "critical")

    def test_critical_priority_at_boundary(self):
        result = calculate_priority("high", 10)
        self.assertEqual(result, "critical")

    def test_high_priority_at_boundary(self):
        result = calculate_priority("low", 10)
        self.assertEqual(result, "high")

    def test_medium_priority_at_boundary(self):
        result = calculate_priority("low", 3)
        self.assertEqual(result, "medium")

    def test_rejects_invalid_urgency(self):
        with self.assertRaises(ValueError):
            calculate_priority("urgent", 5)

    def test_rejects_zero_affected_users(self):
        with self.assertRaises(ValueError):
            calculate_priority("low", 0)

    def test_rejects_non_integer_affected_users(self):
        with self.assertRaises(TypeError):
            calculate_priority("low", "five")

    def test_rejects_boolean_affected_users(self):
        with self.assertRaises(TypeError):
            calculate_priority("low", True)