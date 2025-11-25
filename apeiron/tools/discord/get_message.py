from contextlib import suppress

from discord import Attachment, Client, Message, MessageReference, NotFound, User
from discord.errors import Forbidden
from langchain.tools import tool
from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field


def attachment_to_dict(attachment: Attachment) -> dict:
    """Convert attachment to dictionary representation."""
    attachment_info = {
        "filename": attachment.filename,
        "url": attachment.url,
        "size": attachment.size,
        "content_type": attachment.content_type,
    }
    if attachment.content_type and attachment.content_type.startswith("image/"):
        attachment_info.update(
            {
                "type": "image",
                "dimensions": {
                    "width": attachment.width,
                    "height": attachment.height,
                },
            }
        )
    return attachment_info


def author_to_dict(author: User) -> dict:
    """Convert author to dictionary representation."""
    return {
        "id": str(author.id),
        "name": author.name,
        "display_name": author.display_name,
        "bot": author.bot,
        "avatar_url": str(author.avatar.url) if author.avatar else None,
    }


def reference_to_dict(reference: MessageReference) -> dict:
    """Convert message reference to dictionary representation."""
    ref = reference.resolved
    return {
        "id": str(ref.id),
        "content": ref.content,
        "author": str(ref.author),
        "timestamp": str(ref.created_at),
    }


def to_dict(message: Message) -> dict:
    """Create message data structure."""
    message_data = {
        "content": message.content,
        "id": str(message.id),
        "author": author_to_dict(message.author),
        "channel_id": str(message.channel.id),
        "guild_id": str(message.guild.id) if message.guild else None,
        "timestamp": str(message.created_at),
        "edited_timestamp": str(message.edited_at) if message.edited_at else None,
        "attachments": [
            attachment_to_dict(attachment) for attachment in message.attachments
        ],
    }

    if message.reference and message.reference.resolved:
        message_data["reference"] = reference_to_dict(message.reference)

    return message_data


class GetMessageInput(BaseModel):
    """Arguments for retrieving a specific Discord message."""

    channel_id: int | None = Field(
        None, description="The ID of the channel containing the message"
    )
    message_id: int | None = Field(
        None, description="The ID of the message to retrieve"
    )


def create_get_message_tool(client: Client):
    """Create a tool for retrieving a specific Discord message."""

    @tool(args_schema=GetMessageInput)
    async def get_message(
        channel_id: int | None = None,
        message_id: int | None = None,
        config: RunnableConfig | None = None,
    ) -> dict:
        """Get a specific message.

        Args:
            channel_id: The ID of the channel containing the message.
            message_id: The ID of the message to retrieve.
            config: Optional RunnableConfig object.

        Returns:
            The message information.

        Raises:
            ToolException: If the message is not found or cannot be accessed.
        """
        if not channel_id and config:
            channel_id = config.get("configurable").get("channel_id")
        try:
            channel = None
            with suppress(NotFound):
                channel = await client.fetch_channel(channel_id)
            if not channel:
                return f"Channel {channel_id} not found"
            message = None
            with suppress(NotFound):
                message = await channel.fetch_message(message_id)
            if not message:
                return f"Message {message_id} not found in channel {channel_id}"
            return to_dict(message)
        except Forbidden:
            return f"Cannot access message {message_id} in channel {channel_id}"

    return get_message
