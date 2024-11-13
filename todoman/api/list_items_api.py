from fastapi import APIRouter, HTTPException

from todoman.api.dto.todo_list_dto import TodoListItemDto
from todoman.storage.todo_list_storage import add_item, list_exists, remove_item
from todoman.api.list_items_swagger import delete_items_metadata, post_items_metadata

router = APIRouter()


@router.post('/lists/{list_id}/items', **post_items_metadata)  # type: ignore
async def post_items(list_id: int, dto: TodoListItemDto) -> int:

    # making sure the list exists before proceeding
    if not await list_exists(list_id):
        raise HTTPException(404, 'List not found')

    # converting from DTO to model
    list_item = dto.to_model(0)

    # creating the item on storage and getting its id populated
    await add_item(list_id, list_item)

    # returning the generated item id
    return list_item.id


@router.delete('/lists/{list_id}/items/{item_id}', **delete_items_metadata)  # type: ignore
async def delete_items(list_id: int, item_id: int) -> None:

    # making sure the list exists before proceeding
    if not await list_exists(list_id):
        raise HTTPException(404, 'List not found')

    # removing the item from the list
    await remove_item(list_id, item_id)
