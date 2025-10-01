import asyncio
import logging
import os
from contextlib import asynccontextmanager, suppress

from discord import AutoShardedBot, Client, Intents, Message
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from langchain_core.runnables import RunnableConfig

import apeiron.logging
from apeiron.agents.operator_6o import create_agent, Response
from apeiron.chat_models import create_chat_model
from apeiron.store import create_store
from apeiron.toolkits.discord.toolkit import DiscordToolkit
from apeiron.tools.discord.utils import (
    create_chat_message,
    create_configurable,
    is_bot_mentioned,
    is_bot_message,
    is_private_channel,
)

logger = logging.getLogger(__name__)


class Response(BaseModel):
    """Response format for agent interactions."""

    content: str | None = Field(
        None,
        description="Content of the message to send or reply",
        min_length=1,
        max_length=2000,
    )
    tts: bool | None = Field(
        None, description="Whether to send as text-to-speech message"
    )
    embeds: list[dict] | None = Field(None, description="List of embed dictionaries")
    stickers: list[int] | None = Field(None, description="List of sticker IDs to send")
    suppress_embeds: bool | None = Field(
        None, description="Whether to suppress embeds in this message"
    )
    allowed_mentions: dict | None = Field(
        None, description="Controls which mentions are allowed in the message"
    )
    silent: bool | None = Field(
        None,
        description="Whether to send the message without triggering notifications",
    )


def create_bot():
    # Initialize the MistralAI model
    chat_model = create_chat_model(
        model=os.getenv("APEIRON_MODEL", "mistralai:pixtral-large-2411")
    )
    store = create_store(
        model=os.getenv("APEIRON_EMBEDDING", "mistralai:mistral-embed"),
    )

    # Initialize the Discord client
    bot = AutoShardedBot(intents=Intents.all())
    tools = DiscordToolkit(client=bot).get_tools()
    graph = create_agent(
        tools=tools, model=chat_model, store=store, response_format=Response
    )

    @bot.listen
    async def on_message(message: Message):
        if (
            is_bot_message(bot, message)
            or not is_bot_mentioned(bot, message)
            or not is_private_channel(message)
        ):
            return

        try:
            config: RunnableConfig = {
                "configurable": create_configurable(message),
            }
            if message.guild:
                config["configurable"]["guild_id"] = message.guild.id
            async with message.channel.typing():
                result = await graph.ainvoke(
                    {"messages": [create_chat_message(message)]},
                    config=config,
                )
            response: Response = result["structured_response"]
            await message.channel.send(
                content=response.content,
                tts=response.tts,
                embeds=response.embeds,
                stickers=response.stickers,
                suppress_embeds=response.suppress_embeds,
                allowed_mentions=response.allowed_mentions,
                silent=response.silent,
            )

        except Exception as e:
            logger.error(f"Error handling message event: {str(e)}")

    return bot


def create_api_lifespan(bot: Client):
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Initialize bot on startup
        token = os.getenv("DISCORD_TOKEN")
        if not token:
            raise ValueError("DISCORD_TOKEN environment variable is not set")

        # Start the bot in the background
        bot_task = asyncio.create_task(bot.start(token))

        yield

        # Cleanup on shutdown
        await bot.close()
        bot_task.cancel()
        with suppress(asyncio.CancelledError):
            await bot_task

    return lifespan


def create_api(bot: Client):
    app = FastAPI(lifespan=create_api_lifespan(bot))

    @app.get("/healthz")
    async def liveness_probe():
        return {"status": "ok"}

    @app.get("/readyz")
    async def readiness_probe():
        if bot.is_ready():
            return {"status": "ready"}
        return JSONResponse(content={"status": "not ready"}, status_code=503)

    @app.get("/livez")
    async def startup_probe():
        if not bot.is_closed():
            return {"status": "live"}
        return JSONResponse(content={"status": "not live"}, status_code=503)

    return app


def create_app():
    apeiron.logging.init()
    return create_api(create_bot())
