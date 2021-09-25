#!/usr/bin/env python3

import py
import pytest
import random
import string

import sh

DIR_NAME_LENGTH_MIN = 1
DIR_NAME_LENGTH_MAX = 255

DIR_NAME_ALLOWED_CHARS = string.printable.replace('/', '').replace('.', '')


def get_random_ascii(chars, lower_limit=1, upper_limit=20):
    '''
    Generate random ASCII-encoded string

    chars: string constants - ascii_lowercase, ascii_uppercase, ascii_letters
      digits, punctuation, whitespace, printable
    '''
    rand_length = random.randint(lower_limit, upper_limit)
    return ''.join(random.choice(chars) for _ in range(rand_length))


class TestBasicAscii:

    def test_create_single_dir_ascii_length_min(self, tmpdir):
        '''Create directory with valid ASCII one character long name'''
        # Expected outcome: directory is created

        name_newdir = get_random_ascii(DIR_NAME_ALLOWED_CHARS, DIR_NAME_LENGTH_MIN, DIR_NAME_LENGTH_MIN)
        path_newdir = tmpdir.join(name_newdir)

        # Make sure directory doesn't already exist
        try:
            path_newdir.remove(rec=1, ignore_errors=True)
        except py.error.ENOENT:
            # Ignore 'No such file or directory' error
            pass
        assert not path_newdir.check(), "Failed test setup - directory '{}' not removed".format(path_newdir)

        sh.mkdir(path_newdir)

        # Directory should now exist
        assert path_newdir.check(), "Failed to create directory '{}'".format(path_newdir)

    def test_create_single_dir_ascii_length_random(self, tmpdir):
        '''Create directory with valid random length ASCII name'''
        # Expected outcome: directory is created

        name_newdir = get_random_ascii(DIR_NAME_ALLOWED_CHARS, DIR_NAME_LENGTH_MIN, DIR_NAME_LENGTH_MAX)
        path_newdir = tmpdir.join(name_newdir)

        # Make sure directory doesn't already exist
        try:
            path_newdir.remove(rec=1, ignore_errors=True)
        except py.error.ENOENT:
            # Ignore 'No such file or directory' error
            pass
        assert not path_newdir.check()

        sh.mkdir(path_newdir)

        # Directory should now exist
        assert path_newdir.check(), "Failed to create directory '{}'".format(path_newdir)

    def test_create_single_dir_ascii_length_max(self, tmpdir):
        '''Create directory with valid ASCII max length name'''
        # Expected outcome: directory is created

        name_newdir = get_random_ascii(DIR_NAME_ALLOWED_CHARS, DIR_NAME_LENGTH_MAX, DIR_NAME_LENGTH_MAX)
        path_newdir = tmpdir.join(name_newdir)

        # Make sure directory doesn't already exist
        try:
            path_newdir.remove(rec=1, ignore_errors=True)
        except py.error.ENOENT:
            # Ignore 'No such file or directory' error
            pass
        assert not path_newdir.check(), "Failed test setup - directory not removed"

        sh.mkdir(path_newdir)

        # Directory should now exist
        assert path_newdir.check(), "Failed to create directory '{}'".format(path_newdir)

    def test_create_multiple_dirs(self, tmpdir):
        '''Create multiple directories by single mkdir invocation'''
        # Expected outcome: all directories are created

        # ext4 limit is 64000 items in a directory
        # but bash allows only approx. 26626 parameters to an executable
        DIR_COUNT = 1000

        # Generator for directory names
        def get_path(count):
            for dir_id in range(count):
                name = 'testdir{}'.format(dir_id)
                yield tmpdir.join(name)

        # Make sure directories do not already exist
        for path in get_path(DIR_COUNT):
            try:
                path.remove(rec=1, ignore_errors=True)
            except py.error.ENOENT:
                # Ignore 'No such file or directory' error
                pass
            assert not path.check(), "Failed test setup - directory '{}' not removed".format(path)

        # Pass all directory names at once using argument unpacking
        sh.mkdir(*get_path(DIR_COUNT))

        # Check that all directories were created
        for path in get_path(DIR_COUNT):
            assert path.check(), "Failed to create directory '{}'".format(path)

    def test_create_dir_name_existing(self, tmpdir):
        '''Try creating already existing directory name'''
        # Expected outcome: mkdir fails with exit code 1

        name_newdir = get_random_ascii(DIR_NAME_ALLOWED_CHARS, DIR_NAME_LENGTH_MIN, DIR_NAME_LENGTH_MIN)
        path_newdir = tmpdir.join(name_newdir)

        # Make sure directory doesn't already exist
        try:
            path_newdir.remove(rec=1, ignore_errors=True)
        except py.error.ENOENT:
            # Ignore 'No such file or directory' error
            pass
        assert not path_newdir.check(), "Failed test setup - directory not removed"

        # Using built-in mkdir
        path_newdir.mkdir()

        # Directory should now exist
        assert path_newdir.check(), "Failed test setup - directory does not exist"

        try:
            sh.mkdir(path_newdir)
        except sh.ErrorReturnCode as exc:
            assert exc.exit_code == 1, "Invalid exit code returned ({})".format(exc.exit_code)
        else:
            pytest.fail("Created directory with already existing name")

    def test_create_dir_name_empty(self):
        '''Try creating directory with empty name'''
        # Expected outcome: mkdir fails with exit code 1

        try:
            sh.mkdir('')
        except sh.ErrorReturnCode as exc:
            assert exc.exit_code == 1, "Invalid exit code returned ({})".format(exc.exit_code)
        else:
            pytest.fail("Accepted empty string as directory name")

    def test_create_dir_name_length_over_max(self, tmpdir):
        '''Try creating directory with name longer than allowed'''
        # Expected outcome: mkdir fails with exit code 1

        name_newdir = get_random_ascii(DIR_NAME_ALLOWED_CHARS,
                                       DIR_NAME_LENGTH_MAX+1, DIR_NAME_LENGTH_MAX+1)
        path_newdir = tmpdir.join(name_newdir)

        try:
            sh.mkdir(path_newdir)
        except sh.ErrorReturnCode as exc:
            assert exc.exit_code == 1, "Invalid exit code returned ({})".format(exc.exit_code)
        else:
            pytest.fail("Accepted too long string as directory name")

    def test_create_dir_name_nul_char(self):
        '''Try creating directory name containing NUL character'''
        # Expected outcome: mkdir fails

        # FIXME: Investigate whether created directory name even reaches mkdir
        try:
            sh.mkdir(b'\x31\x00\x32')
        except sh.ForkException as exc:
            assert "ValueError" in str(exc), "ValueError exception not raised"
        else:
            pytest.fail("Accepted directory name containing NUL")

    def test_create_dir_name_forward_slash(self, tmpdir):
        '''Try creating directory name containing forward slash character'''

        name_newdir = "forward/slash"
        path_newdir = tmpdir.join(name_newdir)

        try:
            sh.mkdir(path_newdir)
        except sh.ErrorReturnCode as exc:
            assert exc.exit_code == 1, "Invalid exit code returned ({})".format(exc.exit_code)
        else:
            pytest.fail("Accepted directory name containing forward slash")
