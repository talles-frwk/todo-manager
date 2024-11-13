from fastapi import FastAPI

from todoman.api.lists_api import router as lists_api
from todoman.api.list_items_api import router as list_items_api

app = FastAPI(
    title='TODO Lists Boilerplate',
    description='A FastAPI boilerplate',
    version='0.0.1',
    openapi_tags=[
        {'name': 'TODO Lists', 'description': 'CRUD operations on TODO lists'},
        {'name': 'TODO List Items', 'description': 'Operations for adding and removing list items'}
    ]
)

app.include_router(lists_api)
app.include_router(list_items_api)
