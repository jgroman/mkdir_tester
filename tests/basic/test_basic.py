#!/usr/bin/env python3

import py
import pytest
import random
import string

import sh

MIN_DIR_NAME_LENGTH = 1
MAX_DIR_NAME_LENGTH = 255


def get_random_ascii(chars, lower_limit=1, upper_limit=20):
    '''
    Generate random string

    chars: string constants - ascii_lowercase, ascii_uppercase, ascii_letters
      digits, punctuation, whitespace, printable
    '''
    rand_length = random.randint(lower_limit, upper_limit)
    return ''.join(random.choice(chars) for _ in range(rand_length))


def get_random_unicode(length):

    try:
        get_char = unichr
    except NameError:
        get_char = chr

    # Update this to include code point ranges to be sampled
    include_ranges = [
        (0x0021, 0x0021),
        (0x0023, 0x0026),
        (0x0028, 0x007E),
        (0x00A1, 0x00AC),
        (0x00AE, 0x00FF),
        (0x0100, 0x017F),
        (0x0180, 0x024F),
        (0x2C60, 0x2C7F),
        (0x16A0, 0x16F0),
        (0x0370, 0x0377),
        (0x037A, 0x037E),
        (0x0384, 0x038A),
        (0x038C, 0x038C),
    ]

    alphabet = [
        get_char(code_point) for current_range in include_ranges
        for code_point in range(current_range[0], current_range[1] + 1)
    ]
    return ''.join(random.choice(alphabet) for i in range(length))


class TestBasic:

    def test_create_single_dir_ascii_length_min(self, tmpdir):
        '''Create directory with valid ASCII one character long name'''
        name_newdir = get_random_ascii(string.ascii_lowercase, MIN_DIR_NAME_LENGTH, MIN_DIR_NAME_LENGTH)
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
        assert path_newdir.check()

    def test_create_single_dir_ascii_length_random(self, tmpdir):
        '''Create directory with valid random length ASCII name'''
        name_newdir = get_random_ascii(string.ascii_lowercase, MIN_DIR_NAME_LENGTH, MAX_DIR_NAME_LENGTH)
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
        assert path_newdir.check()

    def test_create_single_dir_ascii_length_max(self, tmpdir):
        '''Create directory with valid ASCII max length name'''
        name_newdir = get_random_ascii(string.ascii_lowercase, MAX_DIR_NAME_LENGTH, MAX_DIR_NAME_LENGTH)
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
        assert path_newdir.check()

    def test_create_dir_name_empty(self):
        '''Try creating directory with empty name'''
        try:
            sh.mkdir('')
        except sh.ErrorReturnCode as exc:
            assert exc.exit_code == 1, "Invalid exit code returned"
        else:
            pytest.fail("Accepted empty string as directory name")

    def test_create_dir_name_length_over_max(self, tmpdir):
        '''Try creating directory with name longer than allowed'''
        name_newdir = get_random_ascii(string.ascii_lowercase, MAX_DIR_NAME_LENGTH+1, MAX_DIR_NAME_LENGTH+1)
        path_newdir = tmpdir.join(name_newdir)

        try:
            sh.mkdir(path_newdir)
        except sh.ErrorReturnCode as exc:
            assert exc.exit_code == 1, "Invalid exit code returned"
        else:
            pytest.fail("Accepted too long string as directory name")

    @pytest.mark.debug
    def test_create_dir_name_nul_char(self):
        '''Try creating directory with NUL char in name'''

        # FIXME
        try:
            sh.mkdir(b'\x31\x00\x32')
        except sh.ForkException as exc:
            assert "ValueError" in str(exc), "ValueError exception not raised"
        else:
            pytest.fail("Accepted string containing NUL")
