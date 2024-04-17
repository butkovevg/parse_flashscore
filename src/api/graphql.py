from fastapi import APIRouter
from strawberry.asgi import GraphQL
from src.service.resolver_graphql import schema

graphql_app = GraphQL(schema)
router = APIRouter(
    prefix='/graphql',
    tags=['graphql'],
)
router.add_route("/graphql", graphql_app)
router.add_websocket_route("/graphql", graphql_app)


@router.get('/')
async def read_root():
    return {"Hello": "World"}
