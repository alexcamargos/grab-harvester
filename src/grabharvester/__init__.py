#!/usr/bin/env python
# encoding: utf-8

# ------------------------------------------------------------------------------
#  Name: __init__.py
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

"""
Grab Harvester - A concurrent batch file downloader.

This package exposes the core DownloadService and DownloadManager classes,
as well as a high-level `download` function for simplified usage.

Logging is disabled by default to avoid polluting the consuming application's output.

To enable logging, use:
    from loguru import logger
    logger.enable('grabharvester')
"""

from pathlib import Path
from typing import List, Sequence, Union

from loguru import logger

from .downloader import DownloadService
from .interfaces import DownloadError, DownloadResult, DownloadTask, FileOperationError, NetworkDownloadError
from .manager import DownloadManager


# NOTE: Disable logging by default when used as a library.
logger.disable('grabharvester')


def download(urls: Sequence[Union[str, DownloadTask]],
             destination_dir: Union[str, Path, None] = None,
             max_threads: int = 5) -> DownloadResult:
    """High-level function to download multiple files concurrently.

    Arguments:
        urls(Sequence[Union[str, DownloadTask]]): A sequence of URLs (strings) or DownloadTask objects.
        destination_dir(Union[str, Path, None]): Optional directory to save files. If None, uses temp
                                                 dir (or uses task specific path). If provided,
                                                 it overrides/sets the directory for string URLs.
        max_threads(int): Number of concurrent threads (default: 5).

    Returns:
        DownloadResult: A tuple containing lists of successful paths and failed tasks.
    """

    # Initialize the download service and manager, then prepare tasks.
    service = DownloadService()
    manager = DownloadManager(service, max_threads=max_threads)

    tasks_to_run = []
    destination_path = Path(destination_dir) if destination_dir else None

    for item in urls:
        if isinstance(item, str):
            if destination_path:
                # If destination_dir is provided, we treat it as a directory.
                # We need to extract the filename from the URL to construct the full path.
                filename = item.split('/')[-1].split('?')[0] or 'downloaded_file'
                download_destination = destination_path / filename
            else:
                download_destination = None

            tasks_to_run.append(DownloadTask(url=item, destination_path=download_destination))
        elif isinstance(item, DownloadTask):
            tasks_to_run.append(item)
        else:
            raise ValueError(f'Invalid item type in urls list: {type(item)}')

    return manager.run(tasks_to_run)


__all__ = [
    'download',
    'DownloadService',
    'DownloadManager',
    'DownloadResult',
    'DownloadTask',
    'DownloadError',
    'NetworkDownloadError',
    'FileOperationError',
]
