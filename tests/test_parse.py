# -*- coding: utf-8 -*-

import unittest

from bio2bel_chebi.models import Chemical
from tests.constants import PopulatedDatabaseMixin


class TestParse(PopulatedDatabaseMixin):

    def test_compound_count(self):
        self.assertEqual(9, self.manager.count_chemicals())
        self.assertEqual(7, self.manager.count_parent_chemicals())
        self.assertEqual(2, self.manager.count_child_chemicals())

    def test_get_compound(self):
        model = self.manager.get_chemical_by_chebi_id('38545')
        self.assertIsNotNone(model)
        self.assertIsInstance(model, Chemical)
        self.assertEqual('rosuvastatin', model.name)
        self.assertIsNotNone(model.inchi)
        self.assertEqual('InChI=1S/C22H28FN3O6S/c1-13(2)20-18(10-9-16(27)11-17(28)12-19(29)'
                         '30)21(14-5-7-15(23)8-6-14)25-22(24-20)26(3)33(4,31)32/h5-10,13,16-'
                         '17,27-28H,11-12H2,1-4H3,(H,29,30)/b10-9+/t16-,17-/m1/s1', model.inchi)

    def test_count_inchis(self):
        self.assertEqual(3, self.manager.count_inchis())

    @unittest.skip
    def test_relation_count(self):
        self.assertEqual(16, self.manager.count_relations())


if __name__ == '__main__':
    unittest.main()
