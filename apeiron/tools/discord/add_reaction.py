from contextlib import suppress

from discord import Client
from discord.errors import Forbidden, NotFound
from discord.message import Message
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from pydantic import BaseModel, Field


class AddReactionInput(BaseModel):
    """Arguments for adding reactions to Discord messages."""

    emoji: str = Field(description="The emoji to react with")
    message_id: int | None = Field(
        None, description="ID of the message to add reaction to"
    )
    channel_id: int | None = Field(
        None, description="ID of the channel containing the message"
    )


def create_add_reaction_tool(client: Client):
    """Create a tool for adding reactions to Discord messages."""

    @tool(args_schema=AddReactionInput)
    async def add_reaction(
        emoji: str,
        message_id: int | None = None,
        channel_id: int | None = None,
        config: RunnableConfig | None = None,
    ) -> str:
        """Add a reaction to a message in a Discord channel.

        Args:
            emoji: The emoji to react with.
            message_id: ID of the message to add reaction to.
            channel_id: ID of the channel containing the message.
            config: Optional RunnableConfig object.

        Returns:
            Confirmation message.

        Raises:
            ToolException: If the reaction addition fails.
        """
        if message_id is None and config:
            message_id = config.get("configurable").get("message_id")
        if channel_id is None and config:
            channel_id = config.get("configurable").get("channel_id")
        try:
            channel = await client.fetch_channel(channel_id)
            target: Message | None = None
            if message_id:
                with suppress(NotFound):
                    target = await channel.fetch_message(message_id)
            if target is None:
                return f"Message {message_id} not found"
            await target.add_reaction(emoji)
            return f"Reaction {emoji} added successfully to message {target.id}"
        except Forbidden as e:
            return f"Failed to add reaction: {str(e)}"

    return add_reaction
