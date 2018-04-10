# -*- coding: utf-8 -*-

import unittest

from tests.constants import PopulatedDatabaseMixin


class TestParse(PopulatedDatabaseMixin):

    def test_compound_count(self):
        self.assertEqual(9, self.manager.count_chemicals())


if __name__ == '__main__':
    unittest.main()
