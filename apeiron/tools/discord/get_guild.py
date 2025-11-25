from contextlib import suppress

from discord import Client, Guild, Role
from discord.errors import Forbidden, NotFound
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from pydantic import BaseModel, Field


def role_to_dict(role: Role) -> dict:
    """Convert role to dictionary representation."""
    return {
        "id": str(role.id),
        "name": role.name,
        "color": role.color.value,
        "position": role.position,
        "permissions": role.permissions.value,
        "hoist": role.hoist,
        "managed": role.managed,
        "mentionable": role.mentionable,
        "created_at": str(role.created_at),
    }


def to_dict(guild: Guild) -> dict:
    """Convert guild to dictionary representation."""
    return {
        "id": str(guild.id),
        "name": guild.name,
        "description": guild.description,
        "owner_id": str(guild.owner_id),
        "member_count": guild.member_count,
        "icon_url": str(guild.icon.url) if guild.icon else None,
        "banner_url": str(guild.banner.url) if guild.banner else None,
        "created_at": str(guild.created_at),
        "premium_tier": guild.premium_tier,
        "premium_subscription_count": guild.premium_subscription_count,
        "roles": [role_to_dict(role) for role in guild.roles],
    }


class GetGuildInput(BaseModel):
    """Arguments for retrieving Discord guild information."""

    guild_id: str | None = Field(
        None, description="Discord guild (server) ID to look up"
    )


def create_get_guild_tool(client: Client):
    """Create a tool for retrieving Discord guild information."""

    @tool(args_schema=GetGuildInput)
    async def get_guild(
        guild_id: str | None = None,
        config: RunnableConfig | None = None,
    ) -> dict:
        """Get guild information.

        Args:
            guild_id: The ID of the guild to retrieve information for.
            config: Optional RunnableConfig object.

        Returns:
            Dictionary representation of the guild.
        """
        if guild_id is None and config:
            guild_id = config.get("configurable").get("guild_id")
        try:
            guild = None
            with suppress(NotFound):
                guild = await client.fetch_guild(int(guild_id))
            if guild is None:
                return f"Guild {guild_id} not found"
            return to_dict(guild)
        except Forbidden as e:
            return f"Failed to get guild: {str(e)}"

    return get_guild
