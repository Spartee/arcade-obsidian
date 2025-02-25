"""
Module providing asynchronous search tool functions for Obsidian notes.

These functions delegate title and content search to the global search index.
Each tool function accepts string parameters (or enums of strings) and hands them
off to Whoosh after necessary conversion.
"""

import asyncio
import logging
from pathlib import Path
from typing import Annotated

from arcade.core.schema import ToolContext
from arcade.sdk import tool

from arcade_obsidian import global_search_index
from arcade_obsidian.constants import OBSIDIAN_VAULT_PATH

logger = logging.getLogger(__name__)

MAX_RESULTS = 10


@tool
async def search_notes_by_title(
    context: ToolContext,
    title_keyword: Annotated[str, "Keyword to search for in the note titles"],
) -> list[str]:
    """Search obsidian notes by title."""
    logger.info("Starting filename search for note titles with keyword: %s", title_keyword)
    if not title_keyword.strip():
        logger.info("Empty title keyword provided, returning empty list.")
        return []

    # Use the vault path to perform a glob search for markdown files whose filenames match the keyword.
    vault_path = Path(OBSIDIAN_VAULT_PATH)
    try:
        # Offload the blocking file system operation to a thread.
        matching_files = await asyncio.to_thread(
            lambda: list(vault_path.rglob(f"*{title_keyword}*.md"))
        )
        matching_files_str = [str(file) for file in matching_files]
        logger.info("Filename search completed: found %d matching files.", len(matching_files_str))
    except Exception:
        logger.exception(
            "Error during filename search for note title with keyword '%s'", title_keyword
        )
        raise
    return matching_files_str


@tool
async def search_notes_by_content(
    context: ToolContext,
    content: Annotated[str, "Keyword to search for in the note content"],
) -> list[str]:
    """
    Search obsidian notes by content. Use when searching for a specific multiple-word
    or sentence within user notes
    """
    matching_files: list[str] = []
    logger.info("Starting content search with keyword: %s", content)
    if not content.strip():
        logger.info("Empty content argument provided, returning empty list.")
        return matching_files
    else:
        try:
            matching_files = await asyncio.to_thread(
                global_search_index.search_by_content, content, MAX_RESULTS
            )
            logger.info("Content search completed: found %d matching files.", len(matching_files))
        except Exception:
            logger.exception("Error during content search for keyword '%s'", content)
            raise

    return matching_files
