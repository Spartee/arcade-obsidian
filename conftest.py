import os
from pathlib import Path

import pytest

from arcade_obsidian import global_search_index


# Ensure the indexing delay variables are set to "0" for tests
@pytest.fixture(scope="session", autouse=True)
def set_index_delays():
    os.environ["INDEX_START_DELAY"] = "0"
    os.environ["INDEX_POLL_INTERVAL"] = "0"
    os.environ["INDEX_STORAGE_PATH"] = os.path.abspath("./test_index.db")
    yield


@pytest.fixture(scope="session")
def data_files():
    base = Path(__file__).parent / "tests" / "data"
    essays_file = base / "essays.md"
    biologynotes_file = base / "biologynotes.md"
    return {
        "essays": essays_file,
        "biologynotes": biologynotes_file,
    }


@pytest.fixture(scope="session")
def setup_index(data_files):
    """
    Clears and rebuilds the shared global search index by indexing the two markdown test files.
    """
    for _, file_path in data_files.items():
        if file_path.exists():
            content = file_path.read_text(encoding="utf8")
            # Index document using the file path as string.
            global_search_index.index_document(str(file_path), content, content[:50])
    yield global_search_index


# New fixture: sample markdown documents for testing index/parse functionality.
@pytest.fixture
def sample_documents():
    return {
        "doc1.md": "---\ntitle: YAML Title Doc1\n---\nContent for doc 1.",
        "doc2.md": "# Header Title Doc2\nSome content.",
        "doc3.md": "No title header or YAML\nJust content here.",
    }


# New fixture: reset the global search index before tests that use it.
@pytest.fixture(autouse=True)
def reset_global_index_before_tests():
    # Clear the persistent global search index by rebuilding with an empty dict.
    global_search_index.rebuild_index({})
