#!/usr/bin/env python
# encoding: utf-8

# ------------------------------------------------------------------------------
#  Name: manager.py
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

"""Manages concurrent downloading of multiple files."""

from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, List

from loguru import logger
from tqdm import tqdm

from .interfaces import DownloadError, DownloadResult, DownloadServiceProtocol, DownloadTask


# pylint: disable=too-few-public-methods
class DownloadManager:
    """Manages concurrent downloading of multiple files.

    Attributes:
        __downloader(DownloadServiceProtocol): The download service used to download files.
        __max_threads(int): The maximum number of concurrent threads.

    Methods:
        run(tasks: List[DownloadTask]) -> DownloadResult: Executes a list of download tasks concurrently.
    """

    def __init__(self, downloader: DownloadServiceProtocol, max_threads: int = 5) -> None:
        """Initializes the DownloadManager with a download service and max threads.

        Arguments:
            downloader(DownloadServiceProtocol): The download service used to download files.
            max_threads(int): The maximum number of concurrent threads (default: 5).
        """

        self.__downloader = downloader
        self.__max_threads = max_threads

    def run(self, tasks: List[DownloadTask]) -> DownloadResult:
        """Executes a list of download tasks concurrently.

        Arguments:
            tasks(List[DownloadTask]): A list of download tasks.

        Returns:
            DownloadResult: A tuple containing lists of successful paths and failed tasks.
        """

        failed_tasks: List[DownloadTask] = []
        successful_paths: List[Path] = []

        if not tasks:
            logger.info('No download tasks to execute.')
            return DownloadResult(successes=[], failures=[])

        # Use ThreadPoolExecutor to manage concurrent downloads.
        with ThreadPoolExecutor(max_workers=self.__max_threads) as executor:
            future_to_task: Dict[Future[Path], DownloadTask] = {
                executor.submit(self.__downloader.download_file, task.url, task.destination_path): task
                for task in tasks
            }

            # Use tqdm to display a progress bar.
            progress_bar = tqdm(as_completed(future_to_task), total=len(tasks), desc='Downloading files...')
            for future in progress_bar:
                task = future_to_task[future]
                try:
                    result = future.result()
                    successful_paths.append(result)
                except DownloadError as error:
                    task_name = task.destination_path.name if task.destination_path else task.url
                    logger.error(f'Task failed for {task_name}: {error}')
                    failed_tasks.append(task)

        return DownloadResult(successes=successful_paths, failures=failed_tasks)
