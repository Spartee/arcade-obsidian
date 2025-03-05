from pathlib import Path

import pytest
from arcade.sdk import ToolContext

from arcade_obsidian import global_search_index
from arcade_obsidian.index.parse import extract_markdown_title
from arcade_obsidian.tools.search import (
    search_notes_by_content,
    search_notes_by_title,
)


# Create a dummy ToolContext (the functions do not depend on it)
class DummyToolContext:
    pass


dummy_context = DummyToolContext()


@pytest.fixture
def sample_notes():
    # Return a dictionary mapping file paths to markdown contents.
    return {
        "/notes/note1.md": "# Title One\nContent alpha",
        "/notes/note2.md": "---\ntitle: Title Two\n---\nContent beta",
        "/notes/note3.md": "No header here plain text",
    }


@pytest.fixture
def index_sample_notes(sample_notes):
    # Rebuild the global index and then index our sample notes.

    global_search_index.rebuild_index({})
    for file_path, content in sample_notes.items():
        title = extract_markdown_title(content, file_path)
        global_search_index.index_document(file_path, content, title)
    return sample_notes


@pytest.fixture
def temp_vault(tmp_path, sample_notes, monkeypatch):
    """
    Create a temporary vault directory with sample markdown files and
    monkey-patch OBSIDIAN_VAULT_PATH to point to this directory.
    """
    vault_dir = tmp_path / "vault"
    vault_dir.mkdir()
    for file_path, content in sample_notes.items():
        file = vault_dir / Path(file_path).name
        file.write_text(content)
    import arcade_obsidian.constants as constants

    monkeypatch.setattr(constants, "OBSIDIAN_VAULT_PATH", str(vault_dir))
    # Also update the constant in the search module so that the correct vault path is used.
    monkeypatch.setattr("arcade_obsidian.tools.search.OBSIDIAN_VAULT_PATH", str(vault_dir))
    return vault_dir


@pytest.mark.asyncio
async def test_search_notes_by_title(temp_vault):
    dummy_context = ToolContext()
    # Search for "note1" — should return note1.md.
    results = await search_notes_by_title(dummy_context, "note1")
    assert any("note1.md" in path for path in results)

    # Search for "note2" — should return note2.md.
    results = await search_notes_by_title(dummy_context, "note2")
    assert any("note2.md" in path for path in results)

    # Nonmatching search should return an empty list.
    results = await search_notes_by_title(dummy_context, "Nonexistent")
    assert results == []


@pytest.mark.asyncio
async def test_search_notes_by_content(index_sample_notes):
    dummy_context = ToolContext()
    results = await search_notes_by_content(dummy_context, "alpha")
    assert any("note1.md" in path for path in results)

    results = await search_notes_by_content(dummy_context, "beta")
    assert any("note2.md" in path for path in results)

    results = await search_notes_by_content(dummy_context, "plain")
    assert any("note3.md" in path for path in results)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "search_fn, query, expected_fragment",
    [
        (search_notes_by_title, "note1", "note1.md"),
        (search_notes_by_title, "note2", "note2.md"),
        (search_notes_by_content, "alpha", "note1.md"),
        (search_notes_by_content, "beta", "note2.md"),
    ],
)
async def test_search_parameterized(
    index_sample_notes, temp_vault, search_fn, query, expected_fragment
):
    dummy_context = ToolContext()
    results = await search_fn(dummy_context, query)
    assert any(expected_fragment in path for path in results)
