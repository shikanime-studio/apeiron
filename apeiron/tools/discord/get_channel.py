from contextlib import suppress

from discord import Client, TextChannel
from discord.errors import Forbidden, NotFound
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from pydantic import BaseModel, Field

from apeiron.tools.discord.list_channels import to_dict


class GetChannelInput(BaseModel):
    """Arguments for retrieving a specific Discord channel."""

    channel_id: int | None = Field(
        None, description="The ID of the channel to retrieve"
    )


def create_get_channel_tool(client: Client):
    """Create a tool for retrieving a specific Discord channel."""

    @tool(args_schema=GetChannelInput)
    async def get_channel(
        channel_id: int | None = None,
        config: RunnableConfig | None = None,
    ) -> dict:
        """Get channel information.

        Args:
            channel_id: The ID of the channel to retrieve.
            config: Optional RunnableConfig object.

        Returns:
            The channel information.

        Raises:
            ToolException: If the channel is not found or not a text channel.
        """
        if channel_id is None and config:
            channel_id = config.get("configurable").get("channel_id")
        try:
            channel = None
            with suppress(NotFound):
                channel = await client.fetch_channel(channel_id)
            if not isinstance(channel, TextChannel):
                return f"Channel {channel_id} not found or not a text channel"
            return to_dict(channel)
        except Forbidden as e:
            return f"Failed to get channel: {str(e)}"

    return get_channel
