from arcade_obsidian.constants import INDEX_POLL_INTERVAL, INDEX_START_DELAY
from arcade_obsidian.index.background import IndexUpdater
from arcade_obsidian.index.index import InMemorySearchIndex

# Create the shared in-memory search index for the entire module.
global_search_index = InMemorySearchIndex()


def start_index_worker() -> IndexUpdater:
    # Use the global in-memory search index
    index_updater = IndexUpdater(
        global_search_index,
        poll_interval=INDEX_POLL_INTERVAL,
        delay_start=INDEX_START_DELAY,
    )
    index_updater.daemon = True  # Set as daemon so it won't block exit
    index_updater.start()
    return index_updater


# Start the background index worker when the module is imported.
global_index_worker = start_index_worker()
