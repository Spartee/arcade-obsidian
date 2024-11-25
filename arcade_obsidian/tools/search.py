import asyncio
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Annotated

import aiofiles
from arcade.core.schema import ToolContext
from arcade.sdk import tool

from arcade_obsidian.constants import OBSIDIAN_VAULT_PATH


@tool()
async def search_notes_by_title(
    context: ToolContext,
    title_keyword: Annotated[str, "Keyword to search for in the note titles"],
) -> list[str]:
    """
    Search notes by title keyword.

    This tool should be used when you need to find all markdown files in the Obsidian vault
    whose filenames contain a specific keyword. It searches recursively through all directories.
    """
    vault_path = Path(OBSIDIAN_VAULT_PATH)
    return [str(file) for file in vault_path.rglob(f"*{title_keyword}*.md")]


async def search_file_for_keyword(note_path: Path, content_keyword: str) -> bool:
    async with aiofiles.open(note_path) as file:
        content = await file.read()
        return content_keyword in content


@tool()
async def search_notes_by_content(
    context: ToolContext,
    content_keyword: Annotated[str, "Keyword to search for in the note content"],
) -> list[str]:
    """
    Search notes that contain a specific keyword in their content.

    This tool should be used when you need to find all markdown files in the Obsidian vault
    that contain a specific keyword in their content.
    """
    vault_path = Path(OBSIDIAN_VAULT_PATH)
    note_paths = list(vault_path.rglob("*.md"))

    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        tasks = [
            loop.run_in_executor(executor, search_file_for_keyword, note_path, content_keyword)
            for note_path in note_paths
        ]
        results = await asyncio.gather(*tasks)

    matching_files = [str(note_path) for note_path, matched in zip(note_paths, results) if matched]
    return matching_files
