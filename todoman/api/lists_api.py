from fastapi import APIRouter, HTTPException

from todoman.api.dto.todo_list_dto import TodoListDto
from todoman.api.lists_swagger import delete_list_metadata, get_list_metadata, get_lists_metadata, post_list_metadata, put_list_metadata
from todoman.entities.todo_list_entities import TodoList, TodoListWithItems
from todoman.storage.todo_list_storage import create_list, delete_list as delete_list_storage, list_exists, retrieve_all_lists, retrieve_list_with_items, update_list

router = APIRouter()


@router.get('/lists', **get_lists_metadata)  # type: ignore
async def get_lists() -> list[TodoList]:

    # retrieving all lists and returning them
    return await retrieve_all_lists()


@router.post('/lists', **post_list_metadata)  # type: ignore
async def post_list(dto: TodoListDto) -> int:

    # converting from DTO to model
    todo_list = dto.to_model(0)

    # creating the list on storage and getting its id populated
    await create_list(todo_list)

    # returning the generated list id
    return todo_list.id


@router.get('/lists/{list_id}', **get_list_metadata)  # type: ignore
async def get_list(list_id: int) -> TodoListWithItems:

    # making sure the list exists before proceeding
    if not await list_exists(list_id):
        raise HTTPException(404, 'List not found')

    # retrieving the list with its items and returning it
    return await retrieve_list_with_items(list_id)


@router.put('/lists/{list_id}', **put_list_metadata)  # type: ignore
async def put_list(list_id: int, dto: TodoListDto) -> None:

    # making sure the list exists before proceeding
    if not await list_exists(list_id):
        raise HTTPException(404, 'List not found')

    # converting from DTO to model
    todo_list = dto.to_model(list_id)

    # updating the list on storage (but not its items)
    await update_list(todo_list)


@router.delete('/lists/{list_id}', **delete_list_metadata)  # type: ignore
async def delete_list(list_id: int) -> None:

    # making sure the list exists before proceeding
    if not await list_exists(list_id):
        raise HTTPException(404, 'List not found')

    # deleting the list and its items
    await delete_list_storage(list_id)
