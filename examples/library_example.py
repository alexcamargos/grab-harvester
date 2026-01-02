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

"""Example script demonstrating the use of Grab Harvester library without logging."""

# pylint: disable=wrong-import-position, duplicate-code

import sys
from pathlib import Path

# Add src to path to run execution
sys.path.append(str(Path(__file__).parent.parent / "src"))

from grabharvester import DownloadManager, DownloadService, DownloadTask

# NOTE: We do NOT enable logger here, so it should be silent


def main():
    """Main function to run the library example."""

    service = DownloadService()
    manager = DownloadManager(service, max_threads=2)

    tasks = [
        DownloadTask(url='https://www.python.org/static/img/python-logo.png'),
        DownloadTask(url='https://www.google.com/images/branding/googlelogo/1x/googlelogo_color_272x92dp.png'),
    ]

    print('Starting downloads (should be silent except for this message)...')
    manager.run(tasks)
    print('Downloads completed (no logs should have shown).')


if __name__ == "__main__":
    main()
