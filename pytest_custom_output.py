#!/usr/bin/env python3
'''

Some parts of code adopted from:

https://github.com/freakboy3742/pytest-tldr
https://github.com/pchomik/pytest-spec

'''


from __future__ import print_function
from os import error
import platform
import sys
import time
import re

import pluggy
import py
import pytest
try:
    from pytest import ExitCode
except ImportError:
    # PyTest <5 compatibility
    from _pytest.main import (
        EXIT_OK,
        EXIT_TESTSFAILED,
    )

    class ExitCode:
        OK = EXIT_OK
        TESTS_FAILED = EXIT_TESTSFAILED


__version__ = '0.1.0'


@pytest.hookimpl(trylast=True)
def pytest_configure(config):
    if getattr(config.option, 'cricket_mode', 'off') == 'off':
        # Unregister the default terminal reporter.
        config.pluginmanager.unregister(name="terminalreporter")

        reporter = CustomReporter(config, sys.stdout)
        config.pluginmanager.register(reporter, "terminalreporter")

        # Force the traceback style to native.
        config.option.tbstyle = 'native'


@pytest.mark.hookwrapper
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    node = getattr(item, 'obj', None)
    if node and item.obj.__doc__:
        report.docstring_summary = str(item.obj.__doc__).lstrip().split("\n")[0].strip()


class CustomReporter:
    def __init__(self, config, file=None):
        self.config = config
        self.file = file if file is not None else sys.stdout

        self.verbosity = self.config.option.verbose
        self.xdist = getattr(self.config.option, 'numprocesses', None) is not None
        self.hasmarkup = False

        self.stats = {}

        # These are needed for compatibility; some plugins
        # rely on the fact that there is a terminalreporter
        # that has specific attributes.
        import _pytest.config
        self._tw = _pytest.config.create_terminal_writer(config, file)
        self.reportchars = None

    ######################################################################
    # Plugin compatibility methods.
    #
    # Plugin overwrites TerminalReporter, but some plugins depend
    # on the outout capabilities of TerminalReporter. Preserve them,
    # to the extent possible.
    ######################################################################

    def write(self, content, **markup):
        self._tw.write(content)

    def write_sep(self, sep, title=None, **markup):
        self.ensure_newline()
        self._tw.sep(sep, title, **markup)

    def ensure_newline(self):
        self._tw.line()

    def write_line(self, line, **markup):
        if not isinstance(line, str):
            line = str(line, errors="replace")
        self.ensure_newline()
        self._tw.line(line, **markup)

    def rewrite(self, line, **markup):
        erase = markup.pop("erase", False)
        if erase:
            fill_count = self._tw.fullwidth - len(line) - 1
            fill = " " * fill_count
        else:
            fill = ""
        line = str(line)
        self._tw.write("\r" + line + fill, **markup)

    def section(self, title, sep="=", **kw):
        self._tw.sep(sep, title, **kw)

    def line(self, msg, **kw):
        self._tw.line(msg, **kw)

    ######################################################################

    def print(self, text='', **kwargs):
        end = kwargs.pop('end', '\n')

        self._tw.write(text)
        self._tw.write(end)
        try:
            if kwargs.pop('flush', False):
                self._tw.flush()
        except AttributeError:
            # pytest 6 introduced a separate flush argument to
            # TerminalWriter.write(), and a standalone TerminalWriter.flush()
            # method. This argument/method didn't exist on pytest 5 and lower;
            # the flush was made implicitly on every write.
            pass

    def pytest_internalerror(self, excrepr):
        for line in str(excrepr).split("\n"):
            self.write_line("INTERNALERROR> " + line)
        return 1

    def pytest_sessionstart(self, session):
        self._starttime = time.time()
        self._n_tests = 0
        self._started = False

    def pytest_runtest_logstart(self, nodeid, location):
        if not self._started:
            self._started = True

    def report_pass(self, report):
        self.stats.setdefault('.', []).append(report)
        self.print('[PASS] {}'.format(report.docstring_summary), flush=True)

    def report_fail(self, report):
        self.stats.setdefault('F', []).append(report)
        reprcrash = getattr(report.longrepr, 'reprcrash', None)
        message = getattr(reprcrash, 'message', None)
        items = re.findall("AssertionError: (.*)$", message, re.MULTILINE)
        self.print('[FAIL] {}, {}'.format(report.docstring_summary, items[0]), flush=True)

    def report_error(self, report):
        self.stats.setdefault('E', []).append(report)
        reprcrash = getattr(report.longrepr, 'reprcrash', 'zzz')
        message = getattr(reprcrash, 'message', 'zzz')
        self.print('[ERROR] {}, {}'.format(report.docstring_summary, message), flush=True)

    def report_skip(self, report):
        self.stats.setdefault('s', []).append(report)
        self.print('[SKIP] {}'.format(report.docstring_summary), flush=True)

    def report_expected_failure(self, report):
        self.stats.setdefault('x', []).append(report)
        self.print('[XFAIL] {}'.format(report.docstring_summary), flush=True)

    def report_unexpected_success(self, report):
        self.stats.setdefault('u', []).append(report)
        self.print('u', end='', flush=True)
        self.print('[UPASS] {}'.format(report.docstring_summary), flush=True)

    def pytest_runtest_logreport(self, report):
        if report.when == 'call':
            self._n_tests += 1

            if report.failed:
                if report.longreprtext == 'Unexpected success':
                    # pytest raw xfail
                    # unittest @unexpectedSuccess, Python 3
                    self.report_unexpected_success(report)
                else:
                    if '\nAssertionError: ' in str(report.longreprtext) \
                            or '\nFailed: ' in str(report.longreprtext):
                        # pytest assertion
                        # unittest self.assert()
                        self.report_fail(report)
                    elif str(report.longreprtext).startswith('[XPASS('):
                        # pytest xfail(strict=True)
                        self.report_unexpected_success(report)
                    else:
                        self.report_error(report)

            elif report.skipped:
                if isinstance(report.longrepr, tuple):
                    self.report_skip(report)
                else:
                    self.report_expected_failure(report)
            else:
                if report.longreprtext == 'Unexpected success':
                    # unittest @unexpectedSuccess, Py2.7
                    self.report_unexpected_success(report)
                else:
                    self.report_pass(report)

        else:
            if report.failed:
                self.report_error(report)
            elif report.skipped:
                if isinstance(report.longrepr, tuple):
                    self.report_skip(report)
                else:
                    self.report_expected_failure(report)

    def pytest_sessionfinish(self, exitstatus):
        errors = self.stats.get('E', [])
        failures = self.stats.get('F', [])
        upasses = self.stats.get('u', [])
        xfails = self.stats.get('x', [])
        skips = self.stats.get('s', [])

        if exitstatus in {ExitCode.OK, ExitCode.TESTS_FAILED}:
            self.config.hook.pytest_terminal_summary(
                config=self.config,
                terminalreporter=self,
                exitstatus=exitstatus,
            )

        problems = []
        if errors:
            problems.append('errors={}'.format(len(errors)))
        if failures:
            problems.append('failures={}'.format(len(failures)))
        if skips:
            problems.append('skipped={}'.format(len(skips)))
        if xfails:
            problems.append('expected failures={}'.format(len(xfails)))
        if upasses:
            problems.append('unexpected successes={}'.format(len(upasses)))

        if self._n_tests:
            self.print()
            if failures or errors or upasses:
                total_fails = len(failures) + len(errors) + len(upasses)
                self.print("/** TEST FAILED: {} ({}), total {} **/".format(total_fails, ", ".join(problems), self._n_tests))
            elif skips or xfails:
                self.print("/** TEST PASSED: {} ({}) **/".format(self._n_tests, ", ".join(problems)))
            else:
                self.print("/** TEST PASSED: {} **/".format(self._n_tests))
