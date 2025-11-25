from contextlib import suppress

from discord import Client, Member
from discord.errors import Forbidden, NotFound
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from pydantic import BaseModel, Field


def to_dict(member: Member) -> dict:
    """Convert member to dictionary representation."""
    return {
        "id": str(member.id),
        "name": member.name,
        "display_name": member.display_name,
        "bot": member.bot,
        "roles": [str(role.id) for role in member.roles],
        "joined_at": str(member.joined_at) if member.joined_at else None,
        "premium_since": str(member.premium_since) if member.premium_since else None,
        "pending": member.pending,
        "nick": member.nick,
        "avatar_url": str(member.avatar.url) if member.avatar else None,
    }


class ListMembersInput(BaseModel):
    """Arguments for listing Discord guild members."""

    guild_id: int | None = Field(
        None, description="Discord guild (server) ID to list members from"
    )
    before: str | None = Field(
        None, description="Optional member ID to list members before"
    )
    after: str | None = Field(
        None, description="Optional member ID to list members after"
    )
    limit: int = Field(100, description="Number of members to retrieve (max 100)")


def create_list_members_tool(client: Client):
    """Create a tool for listing Discord guild members."""

    @tool(args_schema=ListMembersInput)
    async def list_members(
        guild_id: int | None = None,
        before: str | None = None,
        after: str | None = None,
        limit: int = 100,
        config: RunnableConfig | None = None,
    ) -> list[dict]:
        """List members in a guild with optional filters.

        Args:
            guild_id: The ID of the guild to list members from.
            before: Optional member ID to list members before.
            after: Optional member ID to list members after.
            limit: Number of members to retrieve (max 100).
            config: Optional RunnableConfig object.

        Returns:
            List of member dictionaries.

        Raises:
            ToolException: If the members cannot be listed.
        """
        if guild_id is None and config:
            guild_id = config.get("configurable").get("guild_id")
        try:
            guild = None
            with suppress(NotFound):
                guild = await client.fetch_guild(guild_id)
            if guild is None:
                return f"Guild {guild_id} not found"
            kwargs = {"limit": limit}
            if before:
                kwargs["before"] = before
            if after:
                kwargs["after"] = after

            members = await guild.fetch_members(**kwargs).flatten()
            return [to_dict(member) for member in members]
        except (Forbidden, NotFound) as e:
            return f"Failed to list members: {str(e)}"

    return list_members
