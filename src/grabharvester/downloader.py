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

"""Module for downloading files concurrently using multiple threads."""

from pathlib import Path

import httpx
from loguru import logger

from .interfaces import FileOperationError, NetworkDownloadError


class DownloadService:
    """Downloads a single file from a URL using HTTP."""

    def download_file(self, url: str, file_path: Path) -> Path:
        """Download a file from a URL and save it to a local file path.
        
        Arguments:
            url {str} -- The URL of the file to download.
            file_path {Path} -- The local file path where the downloaded file will be saved.

        Returns:
            Path -- The local file path where the downloaded file was saved.

        Raises:
            NetworkDownloadError -- If there was an error during the network request.
            FileOperationError -- If there was an error during file I/O operations.
        """

        try:
            response = httpx.get(url, timeout=30)
            response.raise_for_status()  # Raise an exception for HTTP error status (4xx or 5xx)
        except httpx.RequestError as error:
            # Wrap the specific httpx exception in our custom, more general network error.
            raise NetworkDownloadError(f'Network request for {url} failed: {error}') from error

        try:
            if file_path.exists():
                file_size_local = file_path.stat().st_size
                file_size_remote = int(response.headers.get('content-length', 0))

                if file_size_remote > 0 and file_size_remote == file_size_local:
                    logger.info(f'File already exists and is complete: {file_path.name}')
                    return file_path

            # Ensure parent directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, 'wb') as file:
                for chunk in response.iter_bytes(chunk_size=8192):
                    file.write(chunk)
        except (IOError, OSError) as error:
            # Wrap file system exceptions in our custom file operation error.
            raise FileOperationError(f'File operation for {file_path} failed: {error}') from error

        logger.info(f'Download completed: {file_path.name}')

        return file_path
