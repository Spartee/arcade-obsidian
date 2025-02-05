"""
Module providing the in-memory and persistent search index implementation
using the Whoosh library.

This module supports indexing, searching, rebuilding the index, and persisting the index
to disk. It uses a stemming analyzer and sets up the query parsers with OR-grouping
for more flexible, complex queries.
"""

import logging
import threading
from pathlib import Path

from whoosh import index as whoosh_index
from whoosh.analysis import StemmingAnalyzer
from whoosh.fields import ID, TEXT, Schema
from whoosh.qparser import OrGroup, QueryParser

from arcade_obsidian.constants import INDEX_NAME, INDEX_STORAGE_PATH

# Set up module-level logging.
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Adjust the log level as needed.


class Index:
    """
    Base class for the in-memory and persistent search index.
    """

    def index_document(self, file_path: str, content: str, title: str) -> None:
        """
        Adds or updates a document in the index.
        """
        raise NotImplementedError("Subclass must implement index_document method")

    def remove_document(self, file_path: str) -> None:
        """
        Removes a document from the index.
        """
        raise NotImplementedError("Subclass must implement remove_document method")

    def rebuild_index(self, documents: dict[str, str]) -> None:
        """
        Rebuilds the entire index from a dictionary mapping file paths to document content.
        """
        raise NotImplementedError("Subclass must implement rebuild_index method")

    def search_by_title(self, title_keyword: str, limit: int = 10) -> list[str]:
        """
        Searches the index by the title field using the given keyword.
        """
        raise NotImplementedError("Subclass must implement search_by_title method")

    def search_by_content(self, content_keyword: str, limit: int = 10) -> list[str]:
        """
        Searches the index by the content field using the given keyword.
        """
        raise NotImplementedError("Subclass must implement search_by_content method")

    def save_to_disk(self, storage_path: str) -> None:
        """
        Persists the current in-memory index to disk.
        """
        raise NotImplementedError("Subclass must implement save_to_disk method")


class InMemorySearchIndex(Index):
    """
    Provides an in-memory search index for markdown documents along with optional persistence.

    Attributes:
        index: The Whoosh index object containing the search index.
        lock: A threading.RLock to guard concurrent operations.
        query_parser: QueryParser for content searches.
        title_query_parser: QueryParser for title searches.
    """

    def __init__(self) -> None:
        """
        Initializes the search index.

        Attempts to load a persistent index from disk, if available, otherwise creates
        a new in-memory index. Uses a stemming analyzer for both title and content fields.
        """
        logger.debug("Initializing InMemorySearchIndex")
        self.lock = threading.RLock()

        # Create a stemming analyzer and a schema for the index.
        analyzer = StemmingAnalyzer()
        self.schema = Schema(
            path=ID(unique=True, stored=True),
            title=TEXT(stored=True, analyzer=analyzer),
            content=TEXT(stored=True, analyzer=analyzer),
        )

        # Create or open a persistent index in the given storage directory.
        storage_dir = Path(INDEX_STORAGE_PATH)
        storage_dir.mkdir(parents=True, exist_ok=True)
        try:
            if whoosh_index.exists_in(str(storage_dir), indexname=INDEX_NAME):
                self.index = whoosh_index.open_dir(str(storage_dir), indexname=INDEX_NAME)
                logger.info("Loaded persistent index from disk at %s", INDEX_STORAGE_PATH)
            else:
                self.index = whoosh_index.create_in(
                    str(storage_dir), self.schema, indexname=INDEX_NAME
                )
                logger.info("Created new persistent index at %s", INDEX_STORAGE_PATH)
        except Exception as e:
            logger.warning(
                "Error loading persistent index, falling back to in-memory index. Error: %s", e
            )
            from whoosh.filedb.filestore import RamStorage

            self.index = RamStorage().create_index(self.schema)

        # Use an OR-group so that multiple keywords will be combined with OR by default.
        self.query_parser = QueryParser("content", schema=self.schema, group=OrGroup)
        self.title_query_parser = QueryParser("title", schema=self.schema, group=OrGroup)
        logger.info("InMemorySearchIndex initialized with schema: %s", self.schema)

    def index_document(self, file_path: str, content: str, title: str) -> None:
        """
        Adds or updates a document in the index.
        """
        logger.debug("Indexing/updating document: %s", file_path)
        with self.lock, self.index.writer() as writer:
            writer.update_document(path=file_path, title=title, content=content)
        logger.info("Document indexed: %s", file_path)

    def remove_document(self, file_path: str) -> None:
        """
        Removes a document from the index.
        """
        logger.debug("Removing document: %s", file_path)
        with self.lock, self.index.writer() as writer:
            writer.delete_by_term("path", file_path)
        logger.info("Document removed: %s", file_path)

    def rebuild_index(self, documents: dict[str, str]) -> None:
        """
        Rebuilds the entire index from a dictionary mapping file paths to document content.
        """
        logger.debug("Rebuilding entire search index with %d documents", len(documents))
        with self.lock:
            from whoosh.filedb.filestore import RamStorage

            storage = RamStorage()
            new_index = storage.create_index(self.schema)
            with new_index.writer() as writer:
                for file_path, content in documents.items():
                    title = Path(file_path).stem
                    writer.add_document(path=file_path, title=title, content=content)
            self.index = new_index
        logger.info("Search index rebuilt with %d documents", len(documents))

    def search_by_title(self, title_keyword: str, limit: int = 10) -> list[str]:
        """
        Searches the index by the title field using the given keyword.
        """
        logger.debug("Original title keyword: '%s'", title_keyword)
        if isinstance(title_keyword, bytes):
            title_keyword = title_keyword.decode("utf-8")
        with self.lock, self.index.searcher() as searcher:
            parsed_query = self.title_query_parser.parse(title_keyword)
            logger.debug("Parsed title query: %s", parsed_query)
            results = searcher.search(parsed_query, limit=limit)
            matching_paths = [hit["path"] for hit in results]
            logger.debug("Search by title returned %d results", len(matching_paths))
            return matching_paths

    def search_by_content(self, content: str, limit: int = 10) -> list[str]:
        """
        Searches the index by the content field using the given keyword.
        """
        logger.debug("Original content keyword: '%s'", content)
        if isinstance(content, bytes):
            content = content.decode("utf-8")
        with self.lock, self.index.searcher() as searcher:
            parsed_query = self.query_parser.parse(content)
            logger.debug("Parsed content query: %s", parsed_query)
            results = searcher.search(parsed_query, limit=limit)
            matching_paths = [hit["path"] for hit in results]
            logger.debug("Search by content returned %d results", len(matching_paths))
            return matching_paths

    def save_to_disk(self, storage_path: str) -> None:
        """
        Persists the current in-memory index to disk.
        """
        logger.debug(
            "Saving in-memory index to disk at path: %s using index name: %s",
            storage_path,
            INDEX_NAME,
        )

        storage_dir = Path(storage_path)
        storage_dir.mkdir(parents=True, exist_ok=True)
        try:
            if whoosh_index.exists_in(str(storage_dir), indexname=INDEX_NAME):
                persistent_index = whoosh_index.open_dir(str(storage_dir), indexname=INDEX_NAME)
                logger.info("Opened existing persistent index with name: %s", INDEX_NAME)
            else:
                persistent_index = whoosh_index.create_in(
                    str(storage_dir), self.schema, indexname=INDEX_NAME
                )
                logger.info("Created new persistent index with name: %s", INDEX_NAME)
            with self.lock, persistent_index.writer() as writer:
                count = 0
                with self.index.searcher() as searcher:
                    for doc in searcher.all_stored_fields():
                        writer.update_document(**doc)
                        count += 1
                logger.info("Saved %d documents to persistent index", count)
        except Exception as e:
            logger.exception("Error saving index to disk: %s", e)
