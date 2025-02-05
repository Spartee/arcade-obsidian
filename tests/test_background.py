from pathlib import Path

import pytest

from arcade_obsidian.index.background import IndexUpdater
from arcade_obsidian.index.index import InMemorySearchIndex
from arcade_obsidian.index.parse import extract_markdown_title


def test_background_index_update(tmp_path):
    # Create an initial markdown file in our temporary vault.
    file1 = tmp_path / "test1.md"
    file1.write_text("# Test Title\nInitial content", encoding="utf8")

    # Create a fresh index instance.
    index_instance = InMemorySearchIndex()
    # Instantiate IndexUpdater with zero delays.
    updater = IndexUpdater(index_instance, poll_interval=0, delay_start=0)
    # Override the vault_path to point to our temporary directory.
    updater.vault_path = tmp_path

    # Run an update cycle
    updater.update_index()
    results = index_instance.search_by_title("Test Title")
    assert any("test1.md" in Path(path).name for path in results)

    # Modify the file content.
    file1.write_text("# Test Title\nUpdated content", encoding="utf8")
    updater.update_index()
    results = index_instance.search_by_content("Updated")
    assert any("test1.md" in Path(path).name for path in results)

    # Remove the file and update.
    file1.unlink()
    updater.update_index()
    results = index_instance.search_by_title("Test Title")
    assert not any("test1.md" in Path(path).name for path in results)
