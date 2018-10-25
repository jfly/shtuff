import unittest
from bump_version import bump_version

class TestBumpVersion(unittest.TestCase):
    def test_bump_patch(self):
        self.assertEqual(bump_version('v1.2.3', 'patch'), 'v1.2.4')

    def test_bump_patch_does_not_carry_over(self):
        self.assertEqual(bump_version('v1.2.9', 'patch'), 'v1.2.10')

    def test_bump_minor_resets_patch(self):
        self.assertEqual(bump_version('v1.2.3', 'minor'), 'v1.3.0')

    def test_bump_minor_does_not_carry_over(self):
        self.assertEqual(bump_version('v1.9.3', 'minor'), 'v1.10.0')

    def test_bump_major_resets_minor_and_patch(self):
        self.assertEqual(bump_version('v1.2.3', 'major'), 'v2.0.0')
