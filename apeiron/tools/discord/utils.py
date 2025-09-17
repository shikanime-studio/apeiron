import json

from discord import Client, Message
from langchain_core.messages import AIMessage, HumanMessage

from apeiron.tools.discord.get_message import to_dict


def create_chat_message(message: Message) -> AIMessage | HumanMessage:
    """Create a message event as AIMessage or HumanMessage."""
    message_payload = to_dict(message)
    event_data = {"type": "on_message_event", "payload": message_payload}
    content = []
    for attachment in message.attachments:
        if attachment.content_type and attachment.content_type.startswith("image/"):
            content.append(
                {
                    "type": "image_url",
                    "image_url": attachment.url,
                }
            )
    if content:
        content.append({"type": "text", "text": json.dumps(event_data)})
    else:
        content = json.dumps(event_data)

    return (
        AIMessage(content=content)
        if message.author.bot
        else HumanMessage(content=content)
    )


def create_thread_id(message: Message) -> str:
    """Create a thread ID from a Discord message."""
    if message.guild is None:
        return "/".join(
            [
                "guild",
                "__private__",
                "channel",
                str(message.author.id),
            ]
        )
    if message.thread is None:
        return "/".join(
            [
                "guild",
                str(message.guild.id),
                "channel",
                str(message.channel.id),
            ]
        )
    return "/".join(
        [
            "guild",
            str(message.guild.id),
            "channel",
            str(message.channel.id),
            "thread",
            str(message.thread.id),
        ]
    )


def create_configurable(message: Message) -> dict:
    """Create a configurable object from a Discord message."""
    return {
        "thread_id": create_thread_id(message),
        "message_id": message.id,
        "channel_id": message.channel.id,
        "user_id": message.author.id,
    }


def is_bot_message(client: Client, message: Message) -> bool:
    """Check if the message is from the bot itself."""
    return message.author == client.user


def is_private_channel(message: Message) -> bool:
    """Check if the message is from a private channel."""
    return message.guild is None


def is_bot_mentioned(client: Client, message: Message) -> bool:
    """Check if the message is mentioning or replying to the bot."""
    return client.user.mentioned_in(message)
