"""
Module providing markdown parsing functionality.

This module contains functions for extracting titles from Obsidian markdown files,
including YAML front matter and markdown headers.
"""

import logging
from pathlib import Path

import yaml

logger = logging.getLogger(__name__)


def _extract_yaml_title(content: str) -> str | None:
    """
    Extracts a title from YAML front matter in the given markdown content.

    This function checks if the markdown begins with '---' and, if so, locates the closing '---'.
    It then parses the YAML and returns the "title" value if available.

    Args:
        content (str): The full markdown file content.

    Returns:
        str | None: The extracted title if found, otherwise None.
    """
    if yaml is None:
        return None

    lines = content.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    try:
        # Find the index of the closing '---'
        end_index = next(i for i, line in enumerate(lines[1:], start=1) if line.strip() == "---")
        fm_text = "\n".join(lines[1:end_index])
        data = yaml.safe_load(fm_text)
        if isinstance(data, dict):
            title = data.get("title")
            if isinstance(title, str) and title.strip():
                return title.strip()
    except Exception as e:
        logger.debug("Failed to parse YAML front matter in %s", e)
    return None


def _extract_header_title(content: str) -> str | None:
    """
    Extracts the first markdown header found in the content.

    Iterates over the lines and returns the text following a '#' if found.

    Args:
        content (str): The full markdown file content.

    Returns:
        str | None: The header text if found, otherwise None.
    """
    for line in content.splitlines():
        stripped_line = line.strip()
        if stripped_line.startswith("#"):
            title_candidate = stripped_line.lstrip("#").strip()
            if title_candidate:
                return title_candidate
    return None


def extract_markdown_title(content: str, file_path: str) -> str:
    """
    Extracts a title from the given markdown content using a functional approach.

    The process is as follows:
      1. Attempt to extract a title from YAML front matter.
      2. Attempt to extract the first markdown header.
      3. Fall back to using the file name's stem.

    Args:
        content (str): The full content of the markdown file.
        file_path (str): The path of the file, used to extract the stem as a fallback title.

    Returns:
        str: The extracted title.
    """
    title = _extract_yaml_title(content)
    if title:
        return title
    title = _extract_header_title(content)
    if title:
        return title
    return Path(file_path).stem
