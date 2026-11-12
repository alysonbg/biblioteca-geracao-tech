from ninja import Schema


class UserCreateSchema(Schema):
    username: str
    email: str
    password: str


class UserOutSchema(Schema):
    id: int
    username: str
    email: str


class HealthCheckResponse(Schema):
    status: str
    database: str
    version: str
