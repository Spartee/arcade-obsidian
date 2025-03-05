<div style="display: flex; justify-content: center; align-items: center;">
<img
  src="https://docs.arcade.dev/images/logo/arcade-logo.png"
  style="width: 250px;"
>
<span style="margin: 0 10px;">+</span>
<img
  src="https://images.ctfassets.net/wjg1udsw901v/78Ws2s56LgCLoxkx3Xdcsl/083d00cd84eeec428087bbab65ae3580/obsidian-logo.png"
  style="width: 300px;"
>
</div>
<div style="display: flex; justify-content: center; align-items: center; margin-bottom: 8px;">
    <img src="https://img.shields.io/github/v/release/spartee/arcade-obsidian" alt="GitHub release" style="margin: 0 2px;">
    <img src="https://img.shields.io/badge/python-3.10+-blue.svg" alt="Python version" style="margin: 0 2px;">
    <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License" style="margin: 0 2px;">
    <img src="https://img.shields.io/pypi/v/arcade_obsidian" alt="PyPI version" style="margin: 0 2px;">
</div>
<div style="display: flex; justify-content: center; align-items: center;">
    <a href="https://github.com/spartee/arcade-obsidian" target="_blank">
        <img src="https://img.shields.io/github/stars/spartee/arcade-obsidian" alt="GitHub stars" style="margin: 0 2px;">
    </a>
    <a href="https://github.com/spartee/arcade-obsidian/fork" target="_blank">
        <img src="https://img.shields.io/github/forks/spartee/arcade-obsidian" alt="GitHub forks" style="margin: 0 2px;">
    </a>
</div>

<br>
<br>

# Arcade Obsidian Toolkit

Arcade Obsidian Toolkit provides llm tools for reading, searching and writing to obsidian vaults.

## Features

-   Search and query obsidian vaults with natural language
-   Create, update and delete notes in obsidian vault
-   BM25 search index of markdown files with Whoosh
-   Backup and restore of search index
-   Background updating and file watching

## Install

Install this toolkit using pip:

```bash
pip install arcade_obsidian
```

## Available Tools

To show the tools you can run

```
arcade show --local
```

| Name                          | Description                                                                       |
| ----------------------------- | --------------------------------------------------------------------------------- |
| Obsidian.CreateNote           | Create a new note with given content.                                             |
| Obsidian.UpdateNote           | Update an existing note with new content.                                         |
| Obsidian.SearchNotesByTitle   | Search obsidian notes by title.                                                   |
| Obsidian.SearchNotesByContent | Search obsidian notes by content. Use when searching for a specific multiple-word |
| Obsidian.ListNotes            | List all note filenames in the Obsidian vault.                                    |
| Obsidian.ReadNote             | Read the content of a specific note.                                              |
