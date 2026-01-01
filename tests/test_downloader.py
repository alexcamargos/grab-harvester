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


def test_download_file_already_exists_and_complete(mocker, downloader_service, mock_path):
    """Tests that the download is skipped if the file already exists and is complete."""

    # Step 1 - Arrange
    # Mock the HTTP response with a specific content-length
    mock_response = mocker.Mock()
    mock_response.headers = {'content-length': '1024'}
    mocker.patch('httpx.get', return_value=mock_response)

    # Mock 'open' to ensure it's NOT called
    mock_file_open = mocker.patch('builtins.open', mocker.mock_open())

    # Mock Path.exists to return True
    mocker.patch('pathlib.Path.exists', return_value=True)

    # Mock stat().st_size to match the remote size
    mock_stat_result = mocker.Mock()
    mock_stat_result.st_size = 1024
    mocker.patch('pathlib.Path.stat', return_value=mock_stat_result)

    # Step 2 - Act
    result_path = downloader_service.download_file('http://example.com/file.zip',
                                                   mock_path)

    # Step 3 - Assert
    # The core of this test: ensure open() was never called, skipping the download.
    mock_file_open.assert_not_called()
    # Ensure the function still returns the correct path.
    assert result_path == mock_path


def test_download_file_already_exists_but_incomplete(mocker, downloader_service, mock_path):
    """Tests that the file is re-downloaded if it exists but is incomplete."""

    # Step 1 - Arrange
    # Mock the HTTP response
    mock_response = mocker.Mock()
    mock_response.headers = {'content-length': '2048'}  # Remote file is larger
    mock_response.iter_bytes.return_value = [b'new content']
    mocker.patch('httpx.get', return_value=mock_response)

    # Mock 'open' to check that it IS called
    mock_file_open = mocker.patch('builtins.open', mocker.mock_open())

    # Mock Path.exists to return True
    mocker.patch('pathlib.Path.exists', return_value=True)

    # Mock stat().st_size to be smaller than the remote size
    mock_stat_result = mocker.Mock()
    mock_stat_result.st_size = 1024  # Local file is smaller
    mocker.patch('pathlib.Path.stat', return_value=mock_stat_result)
    mocker.patch('pathlib.Path.mkdir')

    # Step 2 & 3 - Act and Assert
    downloader_service.download_file('http://example.com/file.zip', mock_path)
    # The core of this test: ensure open() WAS called, overwriting the old file.
    mock_file_open.assert_called_once()
    mock_file_open().write.assert_called_once_with(b'new content')


def test_download_file_io_error(mocker, downloader_service, mock_path):
    """Tests handling of file I/O errors during file download."""

    # Step 1 - Arrange
    # Mock the HTTP response (network is working).
    mock_response = mocker.Mock()
    mock_response.raise_for_status.return_value = None
    mocker.patch('httpx.get', return_value=mock_response)

    # Mock 'open' to raise an I/O error (e.g., permission denied).
    mocker.patch('builtins.open', side_effect=IOError('Permission denied'))

    mocker.patch('pathlib.Path.exists', return_value=False)
    mocker.patch('pathlib.Path.mkdir')

    test_url = 'http://example.com/file.zip'

    # Step 2 - Act & Step 3 - Assert
    with pytest.raises(FileOperationError, match='File operation for .* failed'):
        downloader_service.download_file(test_url, mock_path)


def test_download_file_to_temp_dir(mocker, downloader_service):
    """Tests downloading a file to the system temporary directory when no path is provided."""

    # Step 1 - Arrange
    test_url = 'http://example.com/temp_file.zip'
    fake_temp_dir = '/fake/temp'
    expected_path = Path(fake_temp_dir) / 'temp_file.zip'

    # Mock httpx response
    mock_response = mocker.Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.iter_bytes.return_value = [b'data']
    mocker.patch('httpx.get', return_value=mock_response)

    # Mock tempfile.gettempdir to return our fake temp directory.
    mocker.patch('tempfile.gettempdir', return_value=fake_temp_dir)
    # Mock Path.is_dir to return True so the code treats the temp path as a directory.
    mocker.patch('pathlib.Path.is_dir', return_value=True)
    # Mock Path.exists to return False (file doesn't exist yet).
    mocker.patch('pathlib.Path.exists', return_value=False)
    # Mock Path.mkdir to avoid filesystem operations.
    mocker.patch('pathlib.Path.mkdir')
    # Mock open to simulate file writing.
    mock_file_open = mocker.patch('builtins.open', mocker.mock_open())

    # Step 2 - Act
    result_path = downloader_service.download_file(test_url)

    # Step 3 - Assert
    assert result_path == expected_path
    mock_file_open.assert_called_once_with(expected_path, 'wb')
