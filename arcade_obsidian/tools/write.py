from pathlib import Path
from typing import Annotated

from arcade.sdk import ToolContext, tool

from arcade_obsidian.constants import OBSIDIAN_VAULT_PATH


@tool()
async def create_note(
    context: ToolContext,
    filename: Annotated[str, "Filename for the new note"],
    content: Annotated[str, "the content to write into the new note"],
) -> str:
    """
    Create a new note with given content.

    This tool should be used when you need to create a new markdown file in the Obsidian vault
    with specified content.
    """

    # handle filepath variants
    if not Path(filename).is_absolute():
        note_path = Path(OBSIDIAN_VAULT_PATH) / filename
    else:
        note_path = Path(filename)

    # Ensure the filename ends with '.md'
    if note_path.suffix != ".md":
        note_path = note_path.with_suffix(".md")

    if note_path.exists():
        return "Note already exists."
    else:
        # write the content to the file and create the file if it doesn't exist
        # TODO return retryable tool error here
        note_path.parent.mkdir(parents=True, exist_ok=True)
        note_path.touch(exist_ok=True)
        note_path.write_text(content)
        return "Note created successfully."


@tool()
async def update_note(
    context: ToolContext,
    filename: Annotated[str, "Filename of the note"],
    content: Annotated[str, "the content to write into the new note"],
) -> str:
    """
    Update an existing note with new content.

    This tool should be used when you need to update the content of an existing markdown file
    in the Obsidian vault.

    """
    note_path = Path(OBSIDIAN_VAULT_PATH) / filename
    if not note_path.exists():
        return "Note does not exist."
    note_path.write_text(content)
    return "Note updated successfully."
