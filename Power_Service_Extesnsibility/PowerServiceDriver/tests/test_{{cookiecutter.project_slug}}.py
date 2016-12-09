#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for `{{ cookiecutter.driver_name }}`
"""

import unittest

from driver import {{cookiecutter.driver_name}}


class Test{{cookiecutter.driver_name}}(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_000_something(self):
        pass


if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
