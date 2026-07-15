from pydantic import BaseModel, ConfigDict, EmailStr, Field
from pydantic.alias_generators import to_camel


class InSchema(BaseModel):
    """Base for request payloads: accepts the UI's snake_case fields as-is."""

    model_config = ConfigDict(extra="ignore")


class OutSchema(BaseModel):
    """Base for response payloads: serializes Python snake_case fields as camelCase so
    the UI's existing `types.ts` interfaces can consume responses as-is."""

    model_config = ConfigDict(
        alias_generator=to_camel, populate_by_name=True, from_attributes=True
    )


class RegisterRequest(InSchema):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Jane Doe",
                "email": "jane.doe@example.com",
                "password": "correct-horse-battery-staple",
            }
        }
    )

    name: str = Field(min_length=1)
    email: EmailStr
    password: str = Field(min_length=8)


class UserOut(OutSchema):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "8f14e45f-ceea-4d3a-8bd0-8a5f2b1c9e10",
                "name": "Jane Doe",
                "email": "jane.doe@example.com",
                "userType": "standard",
                "isActive": True,
            }
        }
    )

    id: str
    name: str
    email: str
    user_type: str
    is_active: bool
