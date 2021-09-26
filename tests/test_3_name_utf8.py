#!/usr/bin/env python3

import py
import pytest
import random

import sh


class TestNameUtf8:

    DIR_NAME_UTF8_LENGTH_MIN = 1
    DIR_NAME_UTF8_LENGTH_MAX = 63  # UTF-8 data-points can be up to 4 bytes long
    # max allowed filename byte length is 255 bytes

    @staticmethod
    def get_random_utf8_string(lower_limit=1, upper_limit=20):
        '''
        Generate random UTF8-encoded string
        '''

        # Code point ranges to be sampled, update as needed
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
            chr(code_point) for current_range in include_ranges
            for code_point in range(current_range[0], current_range[1] + 1)
        ]
        rand_length = random.randint(lower_limit, upper_limit)

        return ''.join(random.choice(alphabet) for _ in range(rand_length))

    def test_create_dir_utf8(self, tmpdir):
        '''Create directory: random length UTF-8 name'''
        name_newdir = TestNameUtf8.get_random_utf8_string(
            TestNameUtf8.DIR_NAME_UTF8_LENGTH_MIN, TestNameUtf8.DIR_NAME_UTF8_LENGTH_MAX)
        name_newdir = name_newdir.replace('/', '')
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
        assert path_newdir.check(), "Failed to create UTF8 named directory '{}'".format(path_newdir)
