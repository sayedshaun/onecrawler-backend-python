from pydantic import BaseModel, ConfigDict
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


class LogoutRequest(InSchema):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {"refresh_token": "8f14e45f-ceea-4d3a-8bd0-8a5f2b1c9e10"}
        }
    )

    refresh_token: str | None = None


class LogoutOut(OutSchema):
    model_config = ConfigDict(
        json_schema_extra={"example": {"detail": "Logged out successfully"}}
    )

    detail: str
