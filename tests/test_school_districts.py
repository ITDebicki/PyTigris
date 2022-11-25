import unittest
import pytigris

class SDTests(unittest.TestCase):

    def sd(self, year = None, cb = False, state = None):
        df = pytigris.get_school_districts(state = state, year = year, cb = cb)
        self.assertTrue(len(df) > 0, f"get_school_districts(state = {state}, year = {year}, cb = {cb}) does not return full dataframe")

    def test_cb_all(self):
        self.sd(year = 2019, cb = True)

    def test_cb(self):
        for year in [2010, 2016, None]:
            with self.subTest(f"Year = {year}"):
                self.sd(state = 'nm', year = year, cb = True)

    def test_sd(self):
        for year in [2000, 2008, 2009, 2010, 2014, None]:
            with self.subTest(f"Year = {year}"):
                self.sd(state = 'nm', year = year)
    
    def test_value_errors(self):
        for year in [1990, 1995, 2002, 2005]:
            with self.subTest(f"Year = {year}"):
                with self.assertRaises(ValueError):
                    pytigris.get_school_districts(year = year, state = 'ia')

    def test_error_all(self):
        with self.assertRaises(ValueError):
            pytigris.get_school_districts(year = 2020)

    def test_error_all_cb(self):
        with self.assertRaises(ValueError):
            pytigris.get_school_districts(year = 2018, cb = True)

    def test_value_errors_cb(self):
        for year in [1990, 1995, 2000, 2002, 2005, 2012, 2014]:
            with self.subTest(f"Year = {year}"):
                with self.assertRaises(ValueError):
                    pytigris.get_school_districts(year = year, state = 'ia', cb = True)