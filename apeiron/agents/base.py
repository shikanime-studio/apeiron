from pydantic import BaseModel, Field

class Response(BaseModel):
    """Response format for Operator 6O."""

    content: str | None = Field(
        None,
        description="Content of the message to send or reply",
        min_length=1,
        max_length=2000,
    )

