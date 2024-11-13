from asyncio import gather
from typing import Any

from loguru import logger
from redis.asyncio import Redis

from todoman.entities.todo_list_entities import TodoList, TodoListItem, TodoListWithItems


# instantiating the Redis client which is set up to connect on localhost and post 6379 (Redis defaul)
# it does not connect until a command is executed
_client = Redis(decode_responses=True)


async def list_exists(list_id: int) -> bool:

    logger.info(f'Checking if list {list_id} exists on Redis...')

    # Redis key used in this method
    title_key = _title_key(list_id)

    # checking and returning if the list exists
    return await _client.exists(title_key)


async def create_list(todo_list: TodoList) -> None:

    logger.info('Creating list on Redis...')

    # retrieving the next list id and setting up on the object
    last_id_key = _list_last_id_key()
    todo_list.id = await _client.incr(last_id_key)

    # Redis keys used below
    title_key = _title_key(todo_list.id)
    item_last_id_key = _item_last_id_key(todo_list.id)

    # setting up the title and item_last_id for the new list
    # there's no need for setting up an empty items hash
    await _client.set(title_key, todo_list.title)
    await _client.set(item_last_id_key, 0)


async def update_list(todo_list: TodoList) -> None:

    logger.info(f'Updating list {todo_list.id} on Redis...')

    # Redis key used in this method
    title_key = _title_key(todo_list.id)
    
    # setting up the title for the list
    await _client.set(title_key, todo_list.title)


async def delete_list(list_id: int) -> None:

    logger.info(f'Deleting list {list_id} on Redis...')

    # Redis keys used in this method
    title_key = _title_key(list_id)
    items_key = _items_key(list_id)
    item_last_id_key = _item_last_id_key(list_id)

    # deleting the list and its items
    await _client.delete(title_key, items_key, item_last_id_key)


async def add_item(list_id: int, item: TodoListItem) -> TodoListItem:

    logger.info(f'Adding item to list {list_id} on Redis...')

    # Redis keys used in this method
    items_key = _items_key(list_id)
    item_last_id_key = _item_last_id_key(list_id)
    
    # generating the next item id
    item.id = await _client.incr(item_last_id_key)

    # adding to the list the new item
    await _client.hset(items_key, item.id, item.description)  # type: ignore
    
    # returning the generated item id
    return item


async def remove_item(list_id: int, item_id: int) -> None:

    logger.info(f'Removing item {item_id} from list {list_id} on Redis...')

    # Redis key used in this method
    items_key = _items_key(list_id)

    # deleting the item from the list items hash
    await _client.hdel(items_key, item_id)  # type: ignore


async def retrieve_all_lists() -> list[TodoList]:

    logger.info('Retrieving all lists from Redis...')

    # retrieving all existing list ids
    ids = await _retrieve_all_list_ids()

    # retrieving the title for each list id
    coroutines = [_get_list_title(i) for i in ids]
    titles = await gather(*coroutines)

    # returning all existing lists, without its items
    return [TodoList(id=i, title=t) for i, t in zip(ids, titles)]


async def retrieve_list_with_items(list_id) -> TodoListWithItems:

    logger.info(f'Retrieving list {list_id} with its items from Redis...')

    # Redis key used in this method
    title_key = _title_key(list_id)

    # retrieving the list title
    title = await _client.get(title_key)
    
    # retrieving all items for the list
    items = await _retrieve_all_items(list_id)

    # returning the list with its items
    return TodoListWithItems(id=list_id, title=title, items=items)
    

async def _retrieve_all_list_ids() -> list[int]:

    # Redis key used in this method
    title_key = _title_key('*')

    # retrieving all list ids
    keys = await _client.keys(title_key)

    # extracts the id from the Redis key
    def extract_id(key: str) -> int:
        return int(key.split(':')[1])

    # extracting and returning all existing list ids
    return [extract_id(k) for k in keys]


async def _retrieve_all_items(list_id: int) -> list[TodoListItem]:

    # Redis key used in this method
    items_key = _items_key(list_id)
 
    # retrieving all items for the list
    items = await _client.hgetall(items_key)  # type: ignore

    # returning all items for the list
    return [TodoListItem(id=int(i), description=d) for i, d in items.items()]


async def _get_list_title(list_id: int) -> str:

    # Redis key used in this method
    title_key = _title_key(list_id)

    # retrieving and returning the list title
    return await _client.get(title_key)


def _list_last_id_key() -> str:

    # Redis key of type string (but holds an integer)
    # used with INCR to generate the next list id
    return 'list_last_id'


def _title_key(list_id: Any) -> str:

    # Redis key of type string
    return f'list:{list_id}:title'


def _item_last_id_key(list_id: Any) -> str:

    # Redis key of type string (but holds an integer)
    # used with INCR to generate the next item id within a list
    return f'list:{list_id}:item_last_id'


def _items_key(list_id: Any) -> str:

    # Redis key of type hash
    # The hash key is the item incremental id and the value its description
    return f'list:{list_id}:items'
