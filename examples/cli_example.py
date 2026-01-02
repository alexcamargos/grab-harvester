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

"""CLI example demonstrating the usage of Grab Harvester with logging enabled."""

import sys
from pathlib import Path

# Add src to path to run execution
sys.path.append(str(Path(__file__).parent.parent / "src"))

# pylint: disable=wrong-import-position
from loguru import logger

from grabharvester import DownloadManager, DownloadService, DownloadTask

# NOTE: Enable logging for CLI usage.
logger.enable("grabharvester")


def main():
    """Main function to run the CLI example."""

    service = DownloadService()
    manager = DownloadManager(service, max_threads=2)

    tasks = [
        DownloadTask(url='https://www.python.org/static/img/python-logo.png'),
        DownloadTask(url='https://www.google.com/images/branding/googlelogo/1x/googlelogo_color_272x92dp.png'),
    ]

    print('Starting downloads with logging enabled...')
    manager.run(tasks)
    print('Downloads completed.')


if __name__ == "__main__":
    main()
