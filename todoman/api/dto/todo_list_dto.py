from pydantic import BaseModel

from todoman.entities.todo_list_entities import TodoList, TodoListItem


class TodoListDto(BaseModel):
    title: str

    def to_model(self, list_id: int) -> TodoList:
        return TodoList(id=list_id, title=self.title)

    class Config:
        json_schema_extra = {
            'example': {
                'title': 'Shopping List'
            }
        }

class TodoListItemDto(BaseModel):
    description: str

    def to_model(self, item_id: int) -> TodoListItem:
        return TodoListItem(id=item_id, description=self.description)

    class Config:
        json_schema_extra = {
            'example': {
                'description': 'Buy milk'
            }
        }
