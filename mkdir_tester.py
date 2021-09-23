#!/usr/bin/env python3

import click
import os

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS)
def main():
    '''Placeholder'''
    pass


if __name__ == '__main__':
    main()
