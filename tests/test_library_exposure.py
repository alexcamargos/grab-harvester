#!/usr/bin/env python
# encoding: utf-8

# ------------------------------------------------------------------------------
#  Name: test_library_exposure.py
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

"""Tests to verify library exposure and default logging behavior."""

from loguru import logger

import grabharvester
from grabharvester import DownloadManager, DownloadService


def test_library_exposure():
    """Verifies that the package exposes the expected classes and functions."""

    # Step 1 - Arrange & Step 2 - Act
    expected_attributes = [
        'download',
        'DownloadService',
        'DownloadManager',
        'DownloadTask',
        'DownloadResult',
        'DownloadError',
        'NetworkDownloadError',
        'FileOperationError',
    ]
    
    # Step 3 - Assert
    # Check that each expected attribute is exposed in the grabharvester package.
    for attribute in expected_attributes:
        assert hasattr(grabharvester, attribute), f'{attribute} not exposed'

    # Verify that __all__ matches the expected attributes (for wildcard imports).
    assert set(grabharvester.__all__) == set(expected_attributes)


def test_logging_default_behavior():
    """Verifies that logging is disabled by default for the library."""

    # Step 1 - Arrange
    # Create a sink to capture logs.
    captured_logs = []
    sink_id = logger.add(lambda msg: captured_logs.append(msg), level="INFO")

    # Step 2 - Act & Step 3 - Assert
    try:
        # Initialize components.
        service = DownloadService()
        manager = DownloadManager(service)

        # Execute run with empty tasks, which triggers an INFO log if enabled.
        # "No download tasks to execute."
        manager.run([])

        # Verify that nothing was logged (default behavior).
        assert len(captured_logs) == 0, 'Logging should be disabled by default'

    finally:
        # Clean up the sink.
        logger.remove(sink_id)


def test_logging_enable_behavior():
    """Verifies that logging can be enabled explicitly."""

    # Step 1 - Arrange
    captured_logs = []
    sink_id = logger.add(lambda msg: captured_logs.append(msg), level="INFO")

    # Step 2 - Act & Step 3 - Assert
    try:
        # Enable logging for the package.
        logger.enable('grabharvester')

        # Initialize components.
        service = DownloadService()
        manager = DownloadManager(service)

        manager.run([])

        assert len(captured_logs) > 0
        assert 'No download tasks to execute.' in str(captured_logs[0])

    finally:
        # Clean up: remove sink and restore default disabled state.
        logger.remove(sink_id)
        logger.disable('grabharvester')
