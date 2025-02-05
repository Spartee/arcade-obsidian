import pytest

from arcade_obsidian.index.index import InMemorySearchIndex
from arcade_obsidian.index.parse import extract_markdown_title


@pytest.fixture
def sample_docs():
    # Documents map file paths to markdown content.
    return {
        "/path/doc1.md": "---\ntitle: Doc One\n---\nContent for doc one.",
        "/path/doc2.md": "# Doc Two\nSome different content.",
        "/path/doc3.md": "# Random Doc Three\nJust some random content without title header.",
    }


@pytest.fixture
def index_instance():
    # Create a fresh instance for testing.
    return InMemorySearchIndex()


def test_index_document_and_search(index_instance, sample_docs):
    # Index each document
    for path, content in sample_docs.items():
        title = extract_markdown_title(content, path)
        index_instance.index_document(path, content, title)

    # Search by title – expecting to match document 'doc1.md'
    results = index_instance.search_by_title("Doc One")
    assert any("doc1.md" in res for res in results)

    # Search by content – expecting to find 'doc2.md'
    results = index_instance.search_by_content("different")
    assert any("doc2.md" in res for res in results)


def test_remove_document(index_instance):
    # Index a document
    test_path = "/path/unique.md"
    content = "# Unique"
    title = extract_markdown_title(content, test_path)
    index_instance.index_document(test_path, content, title)

    # Confirm it appears in search
    results = index_instance.search_by_title("Unique")
    assert any("unique.md" in res for res in results)

    # Remove and verify absence
    index_instance.remove_document(test_path)
    results_after = index_instance.search_by_title("Unique")
    assert not results_after


def test_rebuild_index(index_instance, sample_docs):
    # First, index some documents.
    for path, content in sample_docs.items():
        title = extract_markdown_title(content, path)
        index_instance.index_document(path, content, title)

    # Rebuild the index with new documents only.
    new_docs = {
        "/new/doc4.md": "### New Doc Four\nThis is some new content.",
        "/new/doc5.md": "---\ntitle: New Doc Five\n---\nContent for doc five.",
    }
    index_instance.rebuild_index(new_docs)

    # Old documents should no longer be found.
    results_old = index_instance.search_by_title("Doc One")
    assert not results_old
    # New document (with YAML title) should be found.
    results_new = index_instance.search_by_title("doc5")
    assert any("doc5.md" in res for res in results_new)


@pytest.mark.parametrize(
    "search_query, expected_fragment",
    [
        ("Doc One", "doc1.md"),
        ("Doc Two", "doc2.md"),
        ("random", "doc3.md"),
    ],
)
def test_search_queries(index_instance, sample_docs, search_query, expected_fragment):
    # Index all documents.
    for path, content in sample_docs.items():
        title = extract_markdown_title(content, path)
        index_instance.index_document(path, content, title)
    results = index_instance.search_by_title(search_query)
    assert any(expected_fragment in res for res in results)
