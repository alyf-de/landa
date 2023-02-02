from unittest import TestCase
from datetime import date

from .birthday import get_age, get_next_birthday, next_birthday_is_decadal

BIRTHDAY = date(2000, 2, 29)

class TestBirthday(TestCase):
	def test_get_age(self):
		self.assertEqual(get_age(), None)

		self.assertEqual(get_age(BIRTHDAY, date(2020, 2, 28)), 19)
		self.assertEqual(get_age(BIRTHDAY, date(2020, 2, 29)), 20)
		self.assertEqual(get_age(BIRTHDAY, date(2020, 3, 1)), 20)

		self.assertEqual(get_age(BIRTHDAY, date(2021, 2, 28)), 20)
		self.assertEqual(get_age(BIRTHDAY, date(2021, 3, 1)), 21)
		self.assertEqual(get_age(BIRTHDAY, date(2021, 3, 2)), 21)

	def test_get_next_birthday(self):
		self.assertEqual(get_next_birthday(), None)
		self.assertEqual(get_next_birthday(BIRTHDAY, date(2019, 1, 1)), date(2019, 3, 1))
		self.assertEqual(get_next_birthday(BIRTHDAY, date(2020, 1, 1)), date(2020, 2, 29))
		self.assertEqual(get_next_birthday(BIRTHDAY, date(2021, 1, 1)), date(2021, 3, 1))

	def test_next_birthday_is_decadal(self):
		self.assertFalse(next_birthday_is_decadal())

		nines = {9, 19, 29, 39, 49, 59, 69, 79, 89, 99, 109, 119}
		for age in nines:
			self.assertTrue(next_birthday_is_decadal(age))

		for age in set(range(120)) - nines:
			self.assertFalse(next_birthday_is_decadal(age))
