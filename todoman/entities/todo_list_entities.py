from typing import Annotated

from annotated_types import Len
from pydantic import BaseModel


class TodoList(BaseModel):
    id: int
    title: Annotated[str, Len(min_length=3, max_length=200)]

    class Config:
        json_schema_extra = {
            'example': {
                'id': 123,
                'title': 'Shopping List'
            }
        }


class TodoListItem(BaseModel):
    id: int
    description: Annotated[str, Len(min_length=3, max_length=200)]

    class Config:
        json_schema_extra = {
            'example': {
                'id': 1,
                'description': 'Buy milk'
            }
        }


class TodoListWithItems(TodoList):
    items: list[TodoListItem]

    class Config:
        json_schema_extra = {
            'example': {
                'id': 123,
                'title': 'Household chores',
                'items': [
                    {'id': 1, 'description': 'Buy milk'},
                    {'id': 2, 'description': 'Mop floor'}
                ]
            }
        }
