#!/usr/bin/env python3

import py
import sh


class TestDirMultiple:
    """
    Class for grouping multiple directory creation tests.
    """

    # Generator for given number of directory paths
    @staticmethod
    def get_path(tmpdir: py.path.local, count: int) -> py.path.local:
        for dir_id in range(count):
            name = 'testdir{}'.format(dir_id)
            yield tmpdir.join(name)

    def test_create_multiple_sibling_dirs(self, tmpdir):
        '''Create directory: multiple siblings'''
        # Expected outcome: all directories are created

        # ext4 limit is 64000 items in a directory
        # but bash allows only approx. 26626 parameters to an executable
        DIR_COUNT = 1000

        # Pass all directory names at once using argument unpacking
        sh.mkdir(*TestDirMultiple.get_path(tmpdir, DIR_COUNT))

        # Check that all directories were created
        for path in TestDirMultiple.get_path(tmpdir, DIR_COUNT):
            assert path.check(), "Failed to create directory '{}'".format(path)
