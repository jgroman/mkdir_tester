# mkdir command testing suite

## Introduction

This testing suite aims to test some parts of `mkdir` shell command functionality with special regard to Oracle Linux 8.

## Quick start

### Prerequisities

This testing suite requires [Python 3.6](https://www.python.org/) or newer. Test scripts are based on [pytest](https://docs.pytest.org/en/latest/) testing framework and for correct function also [sh](https://amoffat.github.io/sh/) package is required.

Installing Python3

```bash
sudo yum install python3
```

Installing packages

```bash
pip3 install pytest sh
```

For detailed information regarding using Python on Oracle Linux please refer to [Oracle® Linux 8 Installing and Managing Python](https://docs.oracle.com/en/operating-systems/oracle-linux/8/python/)

### Running tests

Running complete test suite with customized result output

```bash
pytest
```

Running test suite with standard pytest result output

```bash
pytest -p no:pytest_custom_output
```

## Test approach

## Documentation

Man pages

- [mkdir(1) man page](docs/mkdir-1.txt)
- [mkdir(2) man page](docs/mkdir-2.txt)
- [umask(1) man page](docs/umask-1.txt)
- [chmod(1) man page](docs/chmod-1.txt)
- [environ(7) man page](docs/environ-7.txt)

UTF-8

- [UTF-8 test file](docs/UTF-8-test.txt)

## Extra Notes

### Files and filename restrictions

#### Allowed characters in Linux path

In Unix-like systems, file names are composed of bytes, not characters. At least from the perspective of the kernel and its APIs.

A Unix-like kernel is normally neutral about any byte value but \000 (ASCII: NUL) and \057 (ASCII: slash). In Linux, there are no other restrictions at the filesystem layer, but certain FS drivers and their modes lead to the rejection of some names, usually due to the impossibility of translation. For example, one can’t create a filename with invalid UTF-8 on anything mounted with -o iocharset=utf8 (e. g. types cifs or vfat). None of DOS/Windows-compatible FSes will allow you to make \134 (ASCII: backslash) a part of a name. Or the msdos type will apply DOS restrictions concerning 8.3 names.

Ext3/ext4 isn’t known to have restrictions but aforementioned \000 and \057.

Although it's highly recommend to avoid newlines, tabs, control characters, and the like, and to make sure the filename is valid UTF-8.

#### Path length

On Linux: The maximum length for a file name is 255 bytes (NAME_MAX).

The maximum combined length of both the file name and path name is 4096 bytes. This length matches the PATH_MAX that is supported by the operating system as some syscalls allocate PATH_MAX bytes for certain operations. It is possible to have longer file paths but it is only possible to open such files using shorter relative paths since the full (canonical) path will error out.

#### Directory limit

On ext3, there is technically a limit of 32,000 subdirectories but each directory always includes two links – one to reference itself and another to reference the parent directory – that leaves us with 31,998 to work with.

The default limit on ext4 is 64000 and it can be set by enabling file system feature flag `dir_nlink`.
