import unittest
import pytigris

class ZTCATests(unittest.TestCase):

    def zcta(self, state = None, year = None, cb = False):
        df = pytigris.get_zctas(state = state, year = year, cb = cb)
        self.assertTrue(len(df) > 0, f"zcta(state = {state}, year = {year}, cb = {cb}) does not return full dataframe")

    def test_cb_zcta(self):
        for year in [2000, 2010, 2013, 2015, 2020, None]:
            with self.subTest(f"Year = {year}"):
                self.zcta(year = year, cb = True)

    def test_zcta(self):
        for year in [2000, 2008, 2009, 2010, 2014, 2020, None]:
            with self.subTest(f"Year = {year}"):
                self.zcta(year = year)
    
    def test_zcta_state(self):
        for year in [2000, 2010]:
            with self.subTest(f"Year = {year}"):
                self.zcta(year = year, cb = False, state = 'nm')
    
    def test_zcta_state_cb(self):
        self.zcta(year = 2000, cb = True, state = 'nm')

    def test_filtering_starts_wtih(self):
        df_orig = pytigris.get_zctas(year = 2000, state = 'nm')
        df_filtered = pytigris.get_zctas(year = 2000, state = 'nm', starts_with = '870')
        self.assertGreater(len(df_filtered), 0, "Filtering failed: removed all ZCTAs")
        self.assertLess(len(df_filtered), len(df_orig), "filtering ZCTAs by ZCTA code failed")

    def test_value_errors(self):
        for year in [1990, 1995, 2002, 2005]:
            with self.subTest(f"Year = {year}"):
                with self.assertRaises(ValueError):
                    pytigris.get_zctas(year = year)

    def test_value_errors_cb(self):
        for year in [1995, 2002, 2005, 2012]:
            with self.subTest(f"Year = {year}"):
                with self.assertRaises(ValueError):
                    pytigris.get_zctas(year = year, cb = True)

    def test_value_errors_state(self):
        for year in [1990, 1995, 2002, 2005, 2013, 2020]:
            with self.subTest(f"Year = {year}"):
                with self.assertRaises(ValueError):
                    pytigris.get_zctas(year = year, state = 'co')

    def test_value_errors_state_cb(self):
        for year in [2010, 2002, 2005, 2012]:
            with self.subTest(f"Year = {year}"):
                with self.assertRaises(ValueError):
                    pytigris.get_zctas(year = year, cb = True, state = 'co')
