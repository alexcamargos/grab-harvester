#!/usr/bin/env python
# encoding: utf-8

# ------------------------------------------------------------------------------
#  Name: interfaces.py
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

"""Shared data structures and interface protocols for the application."""

from pathlib import Path
from typing import List, NamedTuple, Protocol


class DownloadError(Exception):
    """Base custom exception for download-related errors."""


class NetworkDownloadError(DownloadError):
    """Exception for errors during the network request part of the download."""


class FileOperationError(DownloadError):
    """Exception for errors during file I/O operations (write, create dir, etc.)."""


# pylint: disable=too-few-public-methods
class DownloadServiceProtocol(Protocol):
    """Defines the protocol for a download service."""

    def download_file(self, url: str, file_path: Path | None = None) -> Path:
        """Download a file from a URL and save it to a local file path."""


class DownloadTask(NamedTuple):
    """Represents a single file download task."""

    url: str
    destination_path: Path | None = None


class DownloadResult(NamedTuple):
    """Result of a download batch execution.

    Attributes:
        successes: List of paths to successfully downloaded files.
        failures: List of tasks that failed.
    """

    successes: List[Path]
    failures: List[DownloadTask]
