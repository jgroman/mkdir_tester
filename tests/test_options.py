#!/usr/bin/env python3

import pytest
import random
import string

import sh


class TestOptions:

    def test_option_help(self):
        """Invoke CLI option '--help'"""
        # Expected outcome: help text is displayed, exit code = 0

        std_output = ''

        def process_output(line):
            nonlocal std_output
            std_output += line

        try:
            sh.mkdir("--help", _out=process_output)
        except sh.ErrorReturnCode:
            pytest.fail("Returned with non-zero exit code")
        else:
            assert 'Usage:' in std_output, "Invalid help text"

    @pytest.mark.debug
    def test_option_version(self):
        """Invoke CLI option '--version'"""
        # Expected outcome: version is displayed, exit code = 0

        std_output = ''

        def process_output(line):
            nonlocal std_output
            std_output += line

        try:
            sh.mkdir("--version", _out=process_output)
        except sh.ErrorReturnCode:
            pytest.fail("Returned with non-zero exit code")
        else:
            assert 'mkdir (GNU coreutils)' in std_output, "Invalid version text"

    def test_option_unknown(self):
        '''Invoke CLI option unknown'''
        # Expected outcome: 'unrecognized option' text is displayed, exit code = 1

        err_output = ''

        def process_error(line):
            nonlocal err_output
            err_output += line

        try:
            sh.mkdir("--aaaaaaaaaa", _err=process_error)
        except sh.ErrorReturnCode as exc:
            assert 'unrecognized option' in err_output, "Invalid STDERR output text"
            assert exc.exit_code == 1, "Invalid exit code returned ({})".format(exc.exit_code)
        else:
            pytest.fail("Failed to return non-zero exit code")

