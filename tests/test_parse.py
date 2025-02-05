import pytest

from arcade_obsidian.index.parse import extract_markdown_title


@pytest.mark.parametrize(
    "content, file_path, expected_title",
    [
        # Title from YAML front matter
        ("---\ntitle: YAML Title\n---\nRest of content", "/path/file.yaml.md", "YAML Title"),
        # Title from markdown header
        ("# Markdown Header Title\nMore content", "/path/file.md", "Markdown Header Title"),
        # Fallback to file stem when no title is found
        ("No title here at all", "/path/filename.md", "filename"),
    ],
)
def test_extract_markdown_title(content, file_path, expected_title):
    title = extract_markdown_title(content, file_path)
    assert title == expected_title
