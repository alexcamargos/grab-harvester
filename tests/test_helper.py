#!/usr/bin/env python
# encoding: utf-8

# ------------------------------------------------------------------------------
#  Name: test_helper.py
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

"""Unit tests for the helper function 'download' in __init__.py."""

# pylint: disable=redefined-outer-name

from pathlib import Path

import pytest

from grabharvester import download
from grabharvester.interfaces import DownloadResult, DownloadTask


@pytest.fixture
def mock_downloader(mocker):
    """Mocks the DownloadManager and DownloadService."""

    mock_manager_cls = mocker.patch('grabharvester.DownloadManager')
    mock_service_cls = mocker.patch('grabharvester.DownloadService')

    mock_instance = mock_manager_cls.return_value
    mock_instance.run.return_value = DownloadResult(successes=[], failures=[])

    return mock_manager_cls, mock_service_cls


def test_download_helper_mixed_inputs(mock_downloader):
    """Tests download() with a mix of strings and DownloadTasks."""

    # Step 1 - Arrange
    mock_manager_cls, _ = mock_downloader
    urls = [
        "http://example.com/file1.zip",
        DownloadTask(url="http://example.com/file2.zip", destination_path=Path("/custom/path.zip")),
    ]

    # Step 2 - Act
    download(urls, max_threads=3)

    # Step 3 - Assert
    # Verify manager initialization arguments.
    mock_manager_cls.assert_called_once()
    _, kwargs = mock_manager_cls.call_args

    assert kwargs['max_threads'] == 3

    # Verify run call arguments.
    manager_instance = mock_manager_cls.return_value
    manager_instance.run.assert_called_once()

    # Extract the first positional argument passed to run(), which should be the list of tasks.
    tasks_arg = manager_instance.run.call_args[0][0]

    assert len(tasks_arg) == 2
    assert tasks_arg[0].url == "http://example.com/file1.zip"
    assert tasks_arg[0].destination_path is None  # Default when no dest_dir provided.
    assert tasks_arg[1].url == "http://example.com/file2.zip"
    assert tasks_arg[1].destination_path == Path("/custom/path.zip")


def test_download_helper_with_destination_dir(mock_downloader):
    """Tests download() with a destination directory overriding string URLs."""

    # Step 1 - Arrange
    mock_manager_cls, _ = mock_downloader

    urls = ["http://example.com/file1.zip"]
    dest_dir = "/tmp/downloads"

    # Step 2 - Act
    download(urls, destination_dir=dest_dir)  # type: ignore

    manager_instance = mock_manager_cls.return_value
    tasks_arg = manager_instance.run.call_args[0][0]

    # Step 3 - Assert

    # Logic should append filename to dest_dir for string URLs.
    expected_path = Path(dest_dir) / "file1.zip"

    assert tasks_arg[0].destination_path == expected_path


def test_download_helper_invalid_input():
    """Tests that download() raises ValueError for invalid input types."""

    # Step 1 - Arrange & Step 2 - Act & Step 3 - Assert
    with pytest.raises(ValueError):
        download([123, "http://valid.com"])  # type: ignore
