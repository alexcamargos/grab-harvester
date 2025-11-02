#!/usr/bin/env python
# encoding: utf-8

# ------------------------------------------------------------------------------
#  Name: test_manager.py
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

"""Unit tests for the DownloadManager class."""

from pathlib import Path

import pytest

from grabharvester.interfaces import (DownloadTask,
                                      FileOperationError,
                                      NetworkDownloadError)
from grabharvester.manager import DownloadManager


@pytest.fixture
def mock_downloader(mocker):
    """Provides a mock downloader service that conforms to the protocol."""
    return mocker.Mock()


@pytest.fixture
def download_manager(mock_downloader):
    """Provides a DownloadManager instance with a mocked downloader."""
    return DownloadManager(downloader=mock_downloader, max_threads=2)


@pytest.fixture
def sample_tasks():
    """Provides a list of sample DownloadTask objects."""
    return [
        DownloadTask(url='http://example.com/file1.zip',
                     destination_path=Path('/tmp/file1.zip')),
        DownloadTask(url='http://example.com/file2.zip',
                     destination_path=Path('/tmp/file2.zip')),
    ]


def test_run_with_no_tasks(download_manager, mock_downloader):
    """Tests that run() handles an empty task list gracefully."""

    # Step 1 - Arrange
    tasks = []

    # Step 2 - Act
    failed_tasks = download_manager.run(tasks)

    # Step 3 - Assert
    assert failed_tasks == []
    mock_downloader.download_file.assert_not_called()


def test_run_all_tasks_succeed(mocker, download_manager, mock_downloader, sample_tasks):
    """Tests the scenario where all download tasks complete successfully."""

    # Step 1 - Arrange
    # Mock tqdm to prevent progress bar output during tests
    mocker.patch('grabharvester.manager.tqdm',
                 side_effect=lambda x,
                 **kwargs: x)

    # Step 2 - Act
    failed_tasks = download_manager.run(sample_tasks)

    # Step 3 - Assert
    assert failed_tasks == []
    assert mock_downloader.download_file.call_count == len(sample_tasks)
    # Verify that the downloader was called with the correct arguments for each task
    mock_downloader.download_file.assert_any_call(sample_tasks[0].url,
                                                  sample_tasks[0].destination_path)
    mock_downloader.download_file.assert_any_call(sample_tasks[1].url,
                                                  sample_tasks[1].destination_path)


@pytest.mark.parametrize("error_to_raise", [NetworkDownloadError, FileOperationError])
def test_run_with_specific_failures(mocker,
                                    download_manager,
                                    mock_downloader,
                                    sample_tasks,
                                    error_to_raise):
    """Tests that the manager correctly handles specific download failures."""

    # Step 1 - Arrange
    # Mock tqdm to prevent progress bar output
    mocker.patch('grabharvester.manager.tqdm',
                 side_effect=lambda x,
                 **kwargs: x)
    # Mock logger and store the mock object to make assertions on it later.
    mock_logger = mocker.patch('grabharvester.manager.logger')

    # The first task will succeed, the second will fail.
    task_to_fail = sample_tasks[1]
    error_message = "Simulated download error"
    mock_downloader.download_file.side_effect = [
        # Result for the first task (success)
        sample_tasks[0].destination_path,
        # Specific exception for the second task (failure)
        error_to_raise(error_message)
    ]

    # Step 2 - Act
    failed_tasks = download_manager.run(sample_tasks)

    # Step 3 - Assert
    # Check that the list of failed tasks contains only the one that failed.
    assert len(failed_tasks) == 1
    assert failed_tasks[0] == task_to_fail

    # Check that the downloader was still called for all tasks.
    assert mock_downloader.download_file.call_count == len(sample_tasks)

    # Check that the error was logged correctly.
    mock_logger.error.assert_called_once()
    # Get the call arguments to inspect the logged message
    log_call_args = mock_logger.error.call_args
    log_message = log_call_args[0][0]
    assert f"Task failed for {task_to_fail.destination_path.name}" in log_message
    assert error_message in log_message
