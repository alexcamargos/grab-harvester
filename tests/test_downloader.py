#!/usr/bin/env python
# encoding: utf-8

# ------------------------------------------------------------------------------
#  Name: test_downloader.py
#  Version: 0.0.1
#
#  Summary: Grab Harvester
#           Unit tests for the DownloadService class.
#
#  Author: Alexsander Lopes Camargos
#  Author-email: alcamargos@vivaldi.net
#
#  License: MIT
# ------------------------------------------------------------------------------

"""Unit tests for the DownloadService class."""

from pathlib import Path

import httpx
import pytest

from grabharvester.downloader import DownloadService
from grabharvester.interfaces import FileOperationError, NetworkDownloadError


@pytest.fixture
def downloader_service():
    """Provides a DownloadService instance for tests."""

    return DownloadService()


@pytest.fixture
def mock_path():
    """Provides a consistent mock Path object for tests."""

    return Path('/fake/dir/file.zip')


def test_download_file_success(mocker, downloader_service, mock_path):
    """Tests successful file download."""

    # Step 1 - Arrange
    # Httpx mock response
    mock_response = mocker.Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.iter_bytes.return_value = [b'file', b'content']

    # Mock httpx.get to return our simulated response.
    mocker.patch('httpx.get', return_value=mock_response)

    # Mock 'open' to simulate writing to a file without touching the disk.
    mock_file_open = mocker.patch('builtins.open', mocker.mock_open())

    # Mock Path.exists to simulate that the file does not exist.
    mocker.patch('pathlib.Path.exists', return_value=False)
    # Mock mkdir to avoid trying to create directories.
    mocker.patch('pathlib.Path.mkdir')

    test_url = 'http://example.com/file.zip'

    # Step 2 - Act
    result_path = downloader_service.download_file(test_url, mock_path)

    # Step 3 - Assert
    # Assert that httpx.get was called with the correct URL.
    httpx.get.assert_called_once_with(test_url, timeout=30)
    # Assert that the file was opened for writing in binary mode ('wb').
    mock_file_open.assert_called_once_with(mock_path, 'wb')
    # Assert that the content was written to the file.
    handle = mock_file_open()
    handle.write.assert_any_call(b'file')
    handle.write.assert_any_call(b'content')

    # Assert that the returned path is the expected one.
    assert result_path == mock_path


def test_download_file_network_error(mocker, downloader_service, mock_path):
    """Tests handling of network errors during file download."""

    # Step 1 - Arrange
    # Mock httpx.get to raise a network exception.
    mocker.patch('httpx.get',
                 side_effect=httpx.RequestError("Connection failed",
                                                request=mocker.Mock()))

    test_url = 'http://example.com/file.zip'

    # Step 2 - Act & Step 3 - Assert
    # Assert that the call to download_file raises the correct exception.
    with pytest.raises(NetworkDownloadError, match="Network request for .* failed"):
        downloader_service.download_file(test_url, mock_path)
