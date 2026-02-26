from strawberry.fastapi import GraphQLRouter

from gym_api.graphql.schema import schema

router = GraphQLRouter(schema, path="/v1/graphql")
