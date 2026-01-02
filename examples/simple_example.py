#!/usr/bin/env python
# encoding: utf-8

# ------------------------------------------------------------------------------
#  Name: downloader.py
#  Version: 0.0.1
#
#  Summary: Grab Harvester
#           A lightweight, concurrent, and robust batch file downloader for Python.
#
#  Author: Alexsander Lopes Camargos
#  Author-email: alcamargos@vivaldi.net
#
#  License: MIT
# ------------------------------------------------------------------------------

"""Demonstrates the simple functional interface of Grab Harvester."""

import sys
from pathlib import Path

# Add src to path to run execution
sys.path.append(str(Path(__file__).parent.parent / "src"))

import grabharvester  # pylint: disable=wrong-import-position


def main():
    """Demonstrates the simple functional interface."""

    print('Downloading files using the simple "download" function...')

    # Simple list of URLs to test downloading.
    urls = [
        'https://www.python.org/static/img/python-logo.png',
        'https://www.google.com/images/branding/googlelogo/1x/googlelogo_color_272x92dp.png',
    ]

    # One-line execution (returns named tuple DownloadResult(successes, failures))
    result = grabharvester.download(urls, destination_dir='downloads', max_threads=4)

    if result.successes:
        print(f'Successfully downloaded {len(result.successes)} files:')

        for path in result.successes:
            print(f' - {path}')

    if not result.failures:
        print('All downloads successful!')
    else:
        print(f'{len(result.failures)} downloads failed.')


if __name__ == "__main__":
    main()
