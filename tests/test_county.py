import unittest
import pytigris

class CountyTests(unittest.TestCase):

    def county(self, states = None, year = None, cb = False):
        df = pytigris.get_counties(states = states, year = year, cb = cb)
        self.assertTrue(len(df) > 0, f"county(states = {states}, year = {year}, cb = {cb}) does not return full dataframe")

    def test_cb_county(self):
        for year in [1990, 2000, 2010, 2013, 2015, None]:
            with self.subTest(f"Year = {year}"):
                self.county(year = year, cb = True)

    def test_county(self):
        for year in [2000, 2008, 2009, 2010, 2014, None]:
            with self.subTest(f"Year = {year}"):
                self.county(year = year)

    def test_county_filtering_list(self):
        df_orig = pytigris.get_counties(year = 2020)
        df_filtered = pytigris.get_counties(states = ['ca', 'or'], year = 2020)
        self.assertGreater(len(df_filtered), 0, "Filtering failed: removed all counties (state list)")
        self.assertLess(len(df_filtered), len(df_orig), "filtering counties by state failed (state list)")

    def test_county_filtering_single(self):
        df_orig = pytigris.get_counties(year = 2020)
        df_filtered = pytigris.get_counties(states = 'az', year = 2020)
        self.assertGreater(len(df_filtered), 0, "Filtering failed: removed all counties (state name)")
        self.assertLess(len(df_filtered), len(df_orig), "Filtering counties by state failed (state name)")

    def test_value_errors(self):
        for year in [1990, 1995, 2002, 2005]:
            with self.subTest(f"Year = {year}"):
                with self.assertRaises(ValueError):
                    pytigris.get_counties(year = year)

    def test_value_errors_cb(self):
        for year in [1995, 2002, 2005, 2012]:
            with self.subTest(f"Year = {year}"):
                with self.assertRaises(ValueError):
                    pytigris.get_counties(year = year, cb = True)
