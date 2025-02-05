from logging import getLogger
from pathlib import Path
from typing import Annotated

from arcade.core.schema import ToolContext
from arcade.sdk import tool

from arcade_obsidian.constants import OBSIDIAN_VAULT_PATH

logger = getLogger(__name__)


@tool()
async def list_notes(context: ToolContext) -> list[str]:
    """
    List all note filenames in the Obsidian vault.

    This tool should be used when you need to retrieve a list of all markdown files
    present in the Obsidian vault directory.
    """
    logger.info("Listing all notes in the Obsidian vault")
    vault_path = Path(OBSIDIAN_VAULT_PATH)

    notes = []
    for file in vault_path.glob("*.md"):
        logger.info(f"Found note: {file}")
        notes.append(str(file))
    return notes


@tool()
async def read_note(context: ToolContext, filename: Annotated[str, "Filename of the note"]) -> str:
    """
    Read the content of a specific note.

    This tool should be used when you need to read the content of a specific markdown file
    in the Obsidian vault.
    """
    note_path = Path(OBSIDIAN_VAULT_PATH) / filename
    logger.info(f"Reading note: {note_path}")
    if not note_path.exists():
        return "Note does not exist."
    return note_path.read_text()
