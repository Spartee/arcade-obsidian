"""
Module providing background index updating functionality.

This module contains classes and functions that automatically update the search index
by scanning the Obsidian vault for markdown files. It extracts indexable data (including
titles parsed from YAML front matter or markdown headers), updates new and modified files,
removes deleted files, and persists changes to disk.
"""

import logging
import threading
import time
from pathlib import Path

from arcade_obsidian.constants import INDEX_STORAGE_PATH, OBSIDIAN_VAULT_PATH
from arcade_obsidian.index.index import InMemorySearchIndex
from arcade_obsidian.index.parse import extract_markdown_title

logger = logging.getLogger(__name__)


class IndexUpdater(threading.Thread):
    """
    Background thread that periodically updates the search index.
    Scans the vault, updates new/changed files in batch, removes deleted files,
    and then persists the index to disk.
    """

    def __init__(
        self,
        index: InMemorySearchIndex,
        poll_interval: float = 10.0,
        delay_start: float = 10.0,
    ) -> None:
        """
        Initializes the IndexUpdater thread.

        Args:
            index: The search index instance to be updated.
            poll_interval: Interval in seconds between scans. Defaults to 10.0.
            delay_start: Delay in seconds before starting the scan loop. Defaults to 10.0.
        """
        super().__init__()
        self.index: InMemorySearchIndex = index
        self.poll_interval: float = poll_interval
        self.delay_start: float = delay_start
        self.stop_event: threading.Event = threading.Event()
        self.vault_path = Path(OBSIDIAN_VAULT_PATH)
        # Dictionary mapping file paths to last modification times.
        self.last_mod_times: dict[str, float] = {}

    def run(self) -> None:
        """
        Runs the index updating loop in the background.

        Waits for an initial delay, then repeatedly scans the vault, updates the index,
        and saves the index to disk until the stop event is set.
        """
        logger.info("IndexUpdater started.")
        time.sleep(self.delay_start)
        while not self.stop_event.is_set():
            try:
                self.update_index()
            except Exception:
                logger.exception("Error updating index")
            time.sleep(self.poll_interval)
        logger.info("IndexUpdater stopped.")

    def update_index(self) -> None:
        """
        Scans the vault, updates the index with new or modified files,
        removes missing files, and persists the index to disk.

        The process involves:
          - Scanning the vault directory for markdown files.
          - Recording their last modification times.
          - Indexing new or updated files.
          - Removing entries for files that no longer exist.
          - Saving the entire index to disk.
        """
        # Scan for markdown files in the vault.
        current_files = list(self.vault_path.rglob("*.md"))
        logger.debug("Found %d markdown files in vault.", len(current_files))
        new_mod_times: dict[str, float] = {}
        for file in current_files:
            try:
                mtime = file.stat().st_mtime
                new_mod_times[str(file)] = mtime
            except Exception:
                logger.exception("Error reading file stat for %s", file)

        # Batch-update documents within a single writer transaction.
        with self.index.lock, self.index.index.writer() as writer:
            # Update or add changed/new files.
            for file_path, mtime in new_mod_times.items():
                if (file_path not in self.last_mod_times) or (
                    self.last_mod_times[file_path] < mtime
                ):
                    try:
                        content = Path(file_path).read_text(encoding="utf8", errors="replace")
                        title = extract_markdown_title(content, file_path)
                        writer.update_document(path=file_path, title=title, content=content)
                        logger.info("Indexed file: %s with title: %s", file_path, title)
                    except Exception:
                        logger.exception("Error indexing file %s", file_path)
            # Remove files that no longer exist.
            for file_path in list(self.last_mod_times.keys()):
                if file_path not in new_mod_times:
                    try:
                        writer.delete_by_term("path", file_path)
                        logger.info("Removed file from index: %s", file_path)
                    except Exception:
                        logger.exception("Error removing file %s from index", file_path)
        self.last_mod_times = new_mod_times

        # Persist the updated index to disk.
        try:
            self.index.save_to_disk(INDEX_STORAGE_PATH)
            logger.info("Saved index to disk at %s", INDEX_STORAGE_PATH)
        except Exception:
            logger.exception("Error saving index to disk")

    def stop(self) -> None:
        """
        Signals the background updater thread to stop.
        """
        self.stop_event.set()
