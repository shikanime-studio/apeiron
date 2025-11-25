from contextlib import suppress

from discord import Client, TextChannel
from discord.errors import Forbidden, NotFound
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from pydantic import BaseModel, Field


def to_dict(channel: TextChannel) -> dict:
    """Convert channel to dictionary representation."""
    return {
        "id": str(channel.id),
        "name": channel.name,
        "type": str(channel.type),
        "position": channel.position,
        "category_id": str(channel.category_id) if channel.category_id else None,
        "topic": channel.topic if hasattr(channel, "topic") else None,
        "nsfw": channel.nsfw if hasattr(channel, "nsfw") else None,
        "created_at": str(channel.created_at),
        "parent_id": str(channel.parent_id) if channel.parent_id else None,
    }


class ListChannelsInput(BaseModel):
    """Input for the DiscordListChannelsTool."""

    guild_id: int | None = Field(
        None, description="Discord guild (server) ID to list channels from"
    )


def create_list_channels_tool(client: Client):
    """Create a tool for listing Discord channels."""

    @tool(args_schema=ListChannelsInput)
    async def list_channels(
        guild_id: int | None = None,
        config: RunnableConfig | None = None,
    ) -> list[dict]:
        """List channels in a guild.

        Args:
            guild_id: ID of the guild to list channels from.
            config: Optional runnable config.

        Returns:
            List of channel dictionaries.
        """
        if guild_id is None and config:
            guild_id = config.get("configurable").get("guild_id")
        try:
            guild = None
            with suppress(NotFound):
                guild = await client.fetch_guild(guild_id)
            if guild is None:
                return f"Guild {guild_id} not found"
            channels = await guild.fetch_channels()
            return [to_dict(channel) for channel in channels]
        except (Forbidden, NotFound) as e:
            return f"Failed to list channels: {str(e)}"

    return list_channels
