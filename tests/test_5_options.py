#!/usr/bin/env python3

import pytest

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

    def test_option_parents_nested_dirs(self, tmpdir):
        '''Create nested directories using '-p/--parents' CLI option'''
        # Expected outcome: Nested directory structure is created, exit code = 0

        PATH_MAX = 4096
        NESTED_COUNT = 10

        nested_name = '/'.join(['testdir{}'.format(i) for i in range(NESTED_COUNT)])

        path_nested = tmpdir.join(nested_name)

        assert len(str(path_nested)) < PATH_MAX, "Incorrect test setup - directory path too long"

        # Try creating nested directories without '-p' CLI option
        try:
            sh.mkdir(path_nested)
        except sh.ErrorReturnCode as exc:
            assert exc.exit_code == 1, "Invalid exit code returned ({})".format(exc.exit_code)
        else:
            pytest.fail("Accepted directory name containing forward slash without '-p/--parents' CLI option")

        # Create nested directories using '-p' CLI option
        try:
            sh.mkdir("-p", path_nested)
        except sh.ErrorReturnCode:
            pytest.fail("Failed to create nested directories using '-p' CLI option")
        else:
            assert path_nested.check(), "Failed to create nested directories using '-p' CLI option"

        # Remove created directories
        first_dir_path = tmpdir.join('testdir0')
        first_dir_path.remove(rec=1)

        # Create nested directories using '--parents' CLI option
        try:
            sh.mkdir("--parents", path_nested)
        except sh.ErrorReturnCode:
            pytest.fail("Failed to create nested directories using '--parents' CLI option")
        else:
            assert path_nested.check(), "Failed to create nested directories using '--parents' CLI option"

    def test_option_parents_suppress_error(self, tmpdir):
        '''Recreate already existing directory using '-p/--parents' CLI option'''
        # Expected outcome: mkdir recreates directory, exit code = 0

        path_newdir = tmpdir.join('testdir')

        # Using built-in mkdir
        path_newdir.mkdir()
        assert path_newdir.check(), "Failed test setup - directory not created"

        # Recreate existing directory using '-p' CLI option
        try:
            sh.mkdir("-p", path_newdir)
        except sh.ErrorReturnCode:
            pytest.fail("Failed to recreate existing directory using '-p' CLI option")
        else:
            # Directory should still exist
            assert path_newdir.check(), "Failed to recreate existing directory using '-p' CLI option"

        # Recreate existing directory using '--parents' CLI option
        try:
            sh.mkdir("--parents", path_newdir)
        except sh.ErrorReturnCode:
            pytest.fail("Failed to recreate existing directory using '--parents' CLI option")
        else:
            # Directory should still exist
            assert path_newdir.check(), "Failed to recreate existing directory using '--parents' CLI option"

    @pytest.mark.debug
    def test_option_delimiter(self, tmpdir):
        '''Create directory name starting with '-' using option list delimiter '--' '''
        # Expected outcome: directory is created, exit code = 0
    
        name_newdir = '-a'
        path_newdir = tmpdir.join(name_newdir)
        tmpdir.chdir()
        
        try:
            sh.mkdir('--', name_newdir)
        except sh.ErrorReturnCode:
            pytest.fail("Failed to create directory '{}'".format(name_newdir))
        else:
            # Directory should exist
            assert path_newdir.check(), "Failed to create directory '{}'".format(name_newdir)

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
