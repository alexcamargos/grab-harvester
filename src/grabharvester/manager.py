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

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List

from loguru import logger
from tqdm import tqdm

from .interfaces import DownloadError, DownloadServiceProtocol, DownloadTask


class DownloadManager:
    """Manages concurrent downloading of multiple files."""

    def __init__(self, downloader: DownloadServiceProtocol, max_threads: int = 5):
        self.__downloader = downloader
        self.__max_threads = max_threads

    def run(self, tasks: List[DownloadTask]) -> List[DownloadTask]:
        """Executes a list of download tasks concurrently."""

        failed_tasks: List[DownloadTask] = []
        if not tasks:
            logger.info('No download tasks to execute.')
            return failed_tasks

        with ThreadPoolExecutor(max_workers=self.__max_threads) as executor:
            future_to_task: Dict[object, DownloadTask] = {
                executor.submit(self.__downloader.download_file,
                                task.url,
                                task.destination_path): task for task in tasks
            }

            progress_bar = tqdm(as_completed(future_to_task), total=len(tasks), desc='Downloading files')
            for future in progress_bar:
                task = future_to_task[future]
                try:
                    future.result()
                except DownloadError as error:
                    logger.error(f'Task failed for {task.destination_path.name}: {error}')
                    failed_tasks.append(task)

        return failed_tasks
