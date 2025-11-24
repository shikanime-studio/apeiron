from discord import Client, Message
from langchain_core.messages import AIMessage, HumanMessage


def format_message(message: Message) -> str:
    """Format Discord message directly as markdown."""
    markdown_content = []

    # Message header
    markdown_content.append("## Discord Message")
    markdown_content.append(f"**ID:** `{message.id}`")
    markdown_content.append(f"**Channel:** `{message.channel.id}`")
    if message.guild:
        markdown_content.append(f"**Guild:** `{message.guild.id}`")
    markdown_content.append(f"**Timestamp:** {message.created_at}")
    if message.edited_at:
        markdown_content.append(f"**Edited:** {message.edited_at}")

    # Author info
    markdown_content.append("\n### Author")
    markdown_content.append(f"**Name:** {message.author.name}")
    if message.author.display_name != message.author.name:
        markdown_content.append(f"**Display Name:** {message.author.display_name}")
    markdown_content.append(f"**ID:** `{message.author.id}`")
    markdown_content.append(f"**Bot:** {'Yes' if message.author.bot else 'No'}")
    if message.author.avatar:
        markdown_content.append(
            f"**Avatar:** [View Avatar]({message.author.avatar.url})"
        )
    # Message content
    if message.content:
        markdown_content.append("\n### Content")
        markdown_content.append(f"```\n{message.content}\n```")

    # Attachments
    if message.attachments:
        markdown_content.append(f"\n### Attachments ({len(message.attachments)})")
        for i, attachment in enumerate(message.attachments, 1):
            markdown_content.append(f"\n**Attachment {i}:**")
            markdown_content.append(f"- **Filename:** {attachment.filename}")
            markdown_content.append(f"- **Size:** {attachment.size} bytes")
            markdown_content.append(
                f"- **Type:** {attachment.content_type or 'Unknown'}"
            )
            markdown_content.append(f"- **URL:** [Download]({attachment.url})")
            if (
                attachment.content_type
                and attachment.content_type.startswith("image/")
                and attachment.width
                and attachment.height
            ):
                markdown_content.append(
                    f"- **Dimensions:** {attachment.width}x{attachment.height}"
                )

    # Referenced message
    if message.reference and message.reference.resolved:
        markdown_content.append("\n### Reply To")
        markdown_content.append(f"**Message ID:** `{message.reference.resolved.id}`")
        markdown_content.append(f"**Author:** {message.reference.resolved.author}")
        markdown_content.append(
            f"**Timestamp:** {message.reference.resolved.created_at}"
        )
        if message.reference.resolved.content:
            markdown_content.append(
                f"**Content:** {message.reference.resolved.content[:100]}{'...' if len(message.reference.resolved.content) > 100 else ''}"
            )
    return "\n".join(markdown_content)


def create_chat_message(message: Message) -> AIMessage | HumanMessage:
    """Create a message event as AIMessage or HumanMessage."""
    text = format_message(message)

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
        content.append({"type": "text", "text": text})
    else:
        content = text

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
