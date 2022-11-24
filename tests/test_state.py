import unittest
import pytigris

class StateTests(unittest.TestCase):

    def state(self, year = None, cb = False):
        df = pytigris.get_states(year = year, cb = cb)
        self.assertTrue(len(df) > 0, f"state(year = {year}, cb = {cb}) does not return full dataframe")

    def test_cb_state(self):
        for year in [1990, 2000, 2010, 2013, 2015, None]:
            with self.subTest(f"Year = {year}"):
                self.state(year = year, cb = True)

    def test_state(self):
        for year in [2000, 2008, 2009, 2010, 2014, None]:
            with self.subTest(f"Year = {year}"):
                self.state(year)

    def test_value_errors(self):
        for year in [1990, 1995, 2002, 2005]:
            with self.subTest(f"Year = {year}"):
                with self.assertRaises(ValueError):
                    pytigris.get_states(year = year)

    def test_value_errors_cb(self):
        for year in [1995, 2002, 2005, 2012]:
            with self.subTest(f"Year = {year}"):
                with self.assertRaises(ValueError):
                    pytigris.get_states(year = year)
        