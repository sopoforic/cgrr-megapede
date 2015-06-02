# Classic Game Resource Reader (CGRR): Parse resources from classic games.
# Copyright (C) 2015  Tracy Poff
#
# This file is part of CGRR.
#
# CGRR is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# CGRR is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with CGRR.  If not, see <http://www.gnu.org/licenses/>.
import os
import unittest

import megapede

class Test_cheesy_megapede_a(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.test_files_path = "test_cheesy_megapede_a"

    def test_export_basic(self):
        """Verify that exporting doesn't die."""
        megapede.export(self.test_files_path)

    def test_roundtrip_scores(self):
        with open(os.path.join(self.test_files_path, megapede.scorefile), "rb") as infile:
            data = infile.read()

        scores = megapede.parse_scores(data)

        self.assertEqual(megapede.unparse_scores(scores), data,
            "roundtripped scores differ from original")
