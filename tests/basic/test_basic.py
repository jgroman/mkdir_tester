#!/usr/bin/env python3

import pytest

from sh import mkdir

@pytest.mark.incremental
class TestBasic:

    def test_create_single_dir(self, tmpdir):
        '''Create single directory'''
        p = tmpdir
        print(p.dirname())
        assert 0
