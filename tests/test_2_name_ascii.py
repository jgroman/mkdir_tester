#!/usr/bin/env python3

import curses.ascii
import pytest
import random
import sh
import string


DIR_NAME_LENGTH_MIN = 1
DIR_NAME_LENGTH_MAX = 255


class TestNameAscii:
    """
    Class for grouping basic directory creation tests using ASCII names.
    """

    @staticmethod
    def get_random_string(chars, lower_limit=1, upper_limit=20):
        '''
        Generate random ASCII-encoded string

        chars: string constants - ascii_lowercase, ascii_uppercase, ascii_letters
        digits, punctuation, whitespace, printable
        '''
        rand_length = random.randint(lower_limit, upper_limit)
        return ''.join(random.choice(chars) for _ in range(rand_length))

    def test_create_dir_name_empty(self):
        '''Create directory: empty name'''
        # Expected outcome: mkdir exits with error code 1

        try:
            sh.mkdir('')
        except sh.ErrorReturnCode as exc:
            assert exc.exit_code == 1, "Invalid exit code returned ({})".format(exc.exit_code)
        else:
            pytest.fail("Accepted empty string as directory name")

    def test_create_dir_name_one_ascii_char(self, tmpdir):
        '''Create directory: all valid ASCII one character names'''
        # Expected outcome: directory is created

        # Characters NUL(0x00), dot(0x2E) and forward slash(0x2F) will be excluded
        # from this testcase. NUL and forward slash are being tested separately.
        # Directory names '.' and '..' are reserved by operating system and
        # usually are already present in every directory.

        for newdir_ord in (*range(1, 0x2E), *range(0x30, 0x80)):    
            path_newdir = tmpdir.join(chr(newdir_ord))

            try:
                sh.mkdir(path_newdir)
            except sh.ErrorReturnCode:
                pytest.fail("Failed to create directory '{}'".format(curses.ascii.unctrl(chr(newdir_ord))))
            else:
                # Directory should now exist
                assert path_newdir.check(), "Failed to create directory '{}'".format(curses.ascii.unctrl(chr(newdir_ord)))

    def test_create_dir_name_one_nul_char(self, tmpdir):
        '''Create directory: name as NUL character only'''
        # Expected outcome:  mkdir exits with error code 1
        # Results may vary depending on used shell

        path_helper = tmpdir.join("testhelper.sh")
        path_helper.write_text("#!/bin/bash\n\nmkdir $'\\x00'", encoding="utf-8")
        path_helper.chmod(0o777)    # Make helper script executable
        path_helper.dirpath().chdir()

        try:
            sh.Command(path_helper)()   # run helper script
        except sh.ErrorReturnCode as exc:
            assert exc.exit_code == 1, "Invalid exit code returned ({})".format(exc.exit_code)
        else:
            pytest.fail("Accepted NUL character as directory name")

    def test_create_dir_name_contains_nul_char(self, tmpdir):
        '''Create directory: name containing NUL character'''
        # Expected outcome: shell dependent, in bash mkdir creates directory name
        # containing part of requested name up to NUL character

        path_helper = tmpdir.join("testhelper.sh")
        path_helper.write_text("#!/bin/bash\n\nmkdir $'first\\x00second'", encoding="utf-8")
        path_helper.chmod(0o777)    # Make helper script executable
        path_helper.dirpath().chdir()

        path_newdir = tmpdir.join("first")

        try:
            sh.Command(path_helper)()   # run helper script
        except sh.ErrorReturnCode:
            pytest.fail("Failed to create directory")
        else:
            assert path_newdir.check(), "Failed to create directory '{}'".format(path_newdir)

    def test_create_dir_name_ascii_length_max(self, tmpdir):
        '''Create directory: max allowed length ASCII name'''
        # Expected outcome: directory is created

        name_newdir = TestNameAscii.get_random_string(
            string.ascii_letters, DIR_NAME_LENGTH_MAX, DIR_NAME_LENGTH_MAX)
        path_newdir = tmpdir.join(name_newdir)

        try:
            sh.mkdir(path_newdir)
        except sh.ErrorReturnCode:
            pytest.fail("Failed to create directory '{}'".format(path_newdir))
        else:
            # Directory should now exist
            assert path_newdir.check(), "Failed to create directory '{}'".format(path_newdir)

    def test_create_dir_name_length_over_max(self, tmpdir):
        '''Create directory: name longer than allowed'''
        # Expected outcome: mkdir fails with exit code 1

        name_newdir = TestNameAscii.get_random_string(string.ascii_letters,
                                                      DIR_NAME_LENGTH_MAX+1, DIR_NAME_LENGTH_MAX+1)
        path_newdir = tmpdir.join(name_newdir)

        try:
            sh.mkdir(path_newdir)
        except sh.ErrorReturnCode as exc:
            assert exc.exit_code == 1, "Invalid exit code returned ({})".format(exc.exit_code)
        else:
            pytest.fail("Accepted too long string as directory name")

    def test_create_dir_name_existing(self, tmpdir):
        '''Create directory: name already exists'''
        # Expected outcome: mkdir fails with exit code 1

        name_newdir = TestNameAscii.get_random_string(
            string.ascii_letters, DIR_NAME_LENGTH_MIN, DIR_NAME_LENGTH_MIN)
        path_newdir = tmpdir.join(name_newdir)

        # Using built-in mkdir
        path_newdir.mkdir()
        assert path_newdir.check(), "Failed test setup - directory does not exist"

        # Testing also against '.' and '..' dirnames which should be already existing
        for name in [name_newdir, '.', '..']:
            path_newdir = tmpdir.join(name)

            try:
                sh.mkdir(path_newdir)
            except sh.ErrorReturnCode as exc:
                assert exc.exit_code == 1, "Invalid exit code returned ({})".format(exc.exit_code)
            else:
                pytest.fail("Created directory with already existing name '{}'".format(name))
