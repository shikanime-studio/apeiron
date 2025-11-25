import asyncio
import logging
import os
from contextlib import asynccontextmanager, suppress

from discord import AutoShardedBot, Client, Intents, Message
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from langchain.agents.structured_output import ProviderStrategy
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import trim_messages
from langchain_core.runnables import Runnable, RunnableConfig
from pydantic import BaseModel

import apeiron.instrumentation
from apeiron.agents import create_agent
from apeiron.chat_message_histories.discord import DiscordChannelChatMessageHistory
from apeiron.chat_models import create_chat_model
from apeiron.messages.utils import trim_messages_images
from apeiron.store import create_store
from apeiron.toolkits.discord.toolkit import DiscordToolkit
from apeiron.tools.discord.utils import (
    create_configurable,
    is_bot_mentioned,
    is_bot_message,
    is_private_channel,
)

logger = logging.getLogger(__name__)


class SendMessageAction(BaseModel):
    content: str


def create_message_handler(bot: Client, graph: Runnable, chat_model: BaseChatModel):
    async def handle_message(message: Message):
        chat_history = DiscordChannelChatMessageHistory(bot)
        await chat_history.load_messages_from_message(message)

        inputs = {
            "messages": trim_messages(
                trim_messages_images(chat_history.messages, max_images=1),
                token_counter=chat_model,
                strategy="last",
                max_tokens=2000,
                start_on="human",
                end_on=("human", "tool"),
                include_system=True,
            )
        }

        config: RunnableConfig = {
            "configurable": create_configurable(message),
        }

        if message.guild:
            config["configurable"]["guild_id"] = message.guild.id

        async with message.channel.typing():
            invoked = await graph.ainvoke(
                inputs,
                config=config,
            )

            structured: SendMessageAction = invoked["structured_response"]

            if isinstance(structured, SendMessageAction):
                await message.channel.send(structured.content)

    return handle_message


def create_bot():
    # Initialize the MistralAI model
    chat_model = create_chat_model(
        model=os.getenv("APEIRON_MODEL", "mistralai:ministral-3b-2410"),
    )
    store = create_store(
        model=os.getenv("APEIRON_EMBEDDING", "mistralai:mistral-embed"),
    )

    # Initialize the Discord client
    bot = AutoShardedBot(intents=Intents.all())
    tools = DiscordToolkit(client=bot).get_tools()

    # Create the agent using the new agents package function
    graph = create_agent(
        agent=os.getenv("APEIRON_AGENT", "operator_6o"),
        tools=tools,
        model=chat_model,
        store=store,
        response_format=SendMessageAction,
    )

    handle_message = create_message_handler(
        bot=bot,
        graph=graph,
        chat_model=chat_model,
    )

    @bot.listen
    async def on_message(message: Message):
        if is_bot_message(bot, message):
            return
        if not is_bot_mentioned(bot, message) and not is_private_channel(message):
            return
        try:
            await handle_message(message)
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
    apeiron.instrumentation.init()
    return create_api(create_bot())
