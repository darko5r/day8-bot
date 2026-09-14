import os

import discord

from engine.adapters.discord_adapter import DiscordEngineAdapter
from engine.commands.models import CommandAction


DISCORD_CREDENTIAL_ENV = "DEEDEE_DISCORD_CREDENTIAL"
FOUNDER_ID_ENV = "DEEDEE_FOUNDER_ID"


def required_environment(name, environ=None):
    source = os.environ if environ is None else environ
    value = source.get(name, "").strip()
    if not value:
        raise RuntimeError(f"missing required environment variable: {name}")
    return value


def make_intents():
    intents = discord.Intents.default()
    intents.message_content = True
    return intents


class DeeDeeDiscordClient(discord.Client):
    def __init__(self, adapter, **kwargs):
        super().__init__(**kwargs)
        self.adapter = adapter

    async def on_ready(self):
        if self.user is None:
            print("Dee Dee connected to Discord.")
            return

        print(
            f"Dee Dee connected as {self.user} "
            f"(user_id={self.user.id})."
        )

    async def on_message(self, message):
        guild = message.guild
        result = self.adapter.process_message(
            message.content or "",
            user_id=message.author.id,
            guild_id=(guild.id if guild is not None else None),
            channel_id=(message.channel.id if guild is not None else None),
            is_bot=bool(getattr(message.author, "bot", False)),
        )

        if result.ignored:
            return

        for chunk in result.messages:
            await message.channel.send(chunk)

        if result.action == CommandAction.SHUTDOWN_SERVICE:
            await self.close()


def main():
    credential = required_environment(DISCORD_CREDENTIAL_ENV)
    founder_user_id = required_environment(FOUNDER_ID_ENV)

    adapter = DiscordEngineAdapter(founder_user_id)
    client = DeeDeeDiscordClient(
        adapter,
        intents=make_intents(),
    )
    client.run(credential)


if __name__ == "__main__":
    main()
