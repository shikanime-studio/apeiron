from discord import Client, Message, TextChannel
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import AIMessage, BaseMessage

from apeiron.tools.discord.utils import create_chat_message


class DiscordChannelChatMessageHistory(BaseChatMessageHistory):
    """Chat message history that stores Discord messages."""

    def __init__(self, discord_client: Client) -> None:
        """Initialize with Discord client."""
        self.discord_client = discord_client
        self.messages: list[BaseMessage] = []

    def add_message(self, message: Message) -> None:
        """Add a Discord message to the store."""
        msg = create_chat_message(message)
        if isinstance(msg, AIMessage):
            self._add_ai_message(msg)
        else:
            self.messages.append(msg)

    def _add_ai_message(self, message: AIMessage) -> None:
        """Add an AI message to the store."""
        if isinstance(self.messages[-1], AIMessage):
            prev = self.messages[-1]
            prev_content = (
                [
                    {"type": "text", "content": msg.content}
                    if isinstance(msg, str)
                    else msg
                    for msg in prev.content
                ]
                if isinstance(prev.content, list)
                else [{"type": "text", "content": prev.content}]
            )
            content = (
                [
                    {"type": "text", "content": msg.content}
                    if isinstance(msg, str)
                    else msg
                    for msg in message.content
                ]
                if isinstance(message.content, list)
                else [{"type": "text", "content": message.content}]
            )
            self.messages[-1] = AIMessage(content=prev_content + content)
        else:
            self.messages.append(message)

    def clear(self) -> None:
        """Clear messages from the store."""
        self.messages = []

    async def load_messages_from_message(
        self, message: Message, limit: int | None = None
    ) -> None:
        """Load messages from a Discord message into the history.
        Args:
            message: The message to load messages from
            limit: Maximum number of messages to load (None for no limit)
        """
        self.clear()
        channel = message.channel
        if channel:
            await self.load_messages_from_channel(channel, limit)

    async def load_messages_from_channel(
        self, channel: TextChannel, limit: int | None = None
    ) -> None:
        """Load messages from a Discord channel into the history.
        Args:
            channel: The channel to load messages from
            limit: Maximum number of messages to load (None for no limit)
        """
        self.clear()
        async for message in channel.history(limit=limit):
            self.add_message(message)

        # Reverse to maintain chronological order
        self.messages.reverse()
