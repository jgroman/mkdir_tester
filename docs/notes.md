# Project notes

## Dependencies

pip install pytest sh click

## Allowed characters in Linux path

In Unix-like systems, file names are composed of bytes, not characters. At least from the perspective of the kernel and its APIs.

A Unix-like kernel is normally neutral about any byte value but \000 (ASCII: NUL) and \057 (ASCII: slash). In Linux, there are no other restrictions at the filesystem layer, but certain FS drivers and their modes lead to the rejection of some names, usually due to the impossibility of translation. For example, one can’t create a filename with invalid UTF-8 on anything mounted with -o iocharset=utf8 (e. g. types cifs or vfat). None of DOS/Windows-compatible FSes will allow you to make \134 (ASCII: backslash) a part of a name. Or the msdos type will apply DOS restrictions concerning 8.3 names.

Ext3/ext4 isn’t known to have restrictions but aforementioned \000 and \057.

Although it's highly recommend to avoid newlines, tabs, control characters, and the like, and to make sure the filename is valid UTF-8.

## Path length

On Linux: The maximum length for a file name is 255 bytes. The maximum combined length of both the file name and path name is 4096 bytes. This length matches the PATH_MAX that is supported by the operating system.

## Directory limit

The limit on ext4 is 64000. Until you enable the file system feature flag dir_nlink.

On ext3, there is technically a limit of 32,000 subdirectories but each directory always includes two links – one to reference itself and another to reference the parent directory – that leaves us with 31,998 to work with.

