import unittest
from bump_version import bump_version

class TestBumpVersion(unittest.TestCase):
    def test_bump_patch(self):
        self.assertEqual(bump_version('v1.0.0', 'patch'), 'v1.0.1')

    def test_bump_patch_does_not_carry_over(self):
        self.assertEqual(bump_version('v1.0.9', 'patch'), 'v1.0.10')

    def test_bump_minor(self):
        self.assertEqual(bump_version('v1.0.0', 'minor'), 'v1.1.0')

    def test_bump_minor_resets_patch(self):
        self.assertEqual(bump_version('v1.0.1', 'minor'), 'v1.1.0')

    def test_bump_minor_does_not_carry_over(self):
        self.assertEqual(bump_version('v1.9.0', 'minor'), 'v1.10.0')

    def test_bump_major(self):
        self.assertEqual(bump_version('v1.0.0', 'major'), 'v2.0.0')

    def test_bump_major_resets_minor_and_patch(self):
        self.assertEqual(bump_version('v1.1.1', 'major'), 'v2.0.0')
