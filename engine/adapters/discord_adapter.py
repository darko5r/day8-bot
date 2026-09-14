import time
from dataclasses import dataclass

from engine.commands.models import CommandAction, CommandRuntime
from engine.commands.service import handle_command
from engine.conversation import handle_message
from engine.memory import MemoryStore
from engine.trust.discord import (
    DiscordTrustContext,
    bind_discord_identity,
    discord_stable_id,
)
from engine.trust.service import TrustService


DISCORD_MESSAGE_LIMIT = 1900


@dataclass(frozen=True)
class DiscordDispatchResult:
    messages: tuple[str, ...] = ()
    action: CommandAction = CommandAction.NONE
    action_value: int | None = None
    ignored: bool = False


def split_discord_text(text, limit=DISCORD_MESSAGE_LIMIT):
    if not isinstance(limit, int) or isinstance(limit, bool) or limit <= 0:
        raise ValueError("limit must be a positive integer")

    if not text:
        return ()

    chunks = []
    remaining = text

    while len(remaining) > limit:
        cut = remaining.rfind("\n", 0, limit + 1)
        if cut <= 0:
            cut = limit

        chunks.append(remaining[:cut])

        if cut < len(remaining) and remaining[cut] == "\n":
            remaining = remaining[cut + 1 :]
        else:
            remaining = remaining[cut:]

    if remaining:
        chunks.append(remaining)

    return tuple(chunks)


class DiscordEngineAdapter:
    def __init__(
        self,
        founder_user_id,
        *,
        clock=time.monotonic,
        message_limit=DISCORD_MESSAGE_LIMIT,
    ):
        if not callable(clock):
            raise TypeError("clock must be callable")
        if (
            not isinstance(message_limit, int)
            or isinstance(message_limit, bool)
            or message_limit <= 0
        ):
            raise ValueError("message_limit must be a positive integer")

        self.clock = clock
        self.started_at = clock()
        self.message_limit = message_limit
        self.memory_store = MemoryStore()
        self.trust_service = TrustService(
            founder_id=discord_stable_id(founder_user_id),
        )

    @property
    def founder_id(self):
        return self.trust_service.founder_id

    def _runtime_for(self, context):
        return CommandRuntime(
            started_at=self.started_at,
            clock=self.clock,
            protocol="discord",
            actor_id=context.stable_id,
            trust_service=self.trust_service,
            authorization_scope=context.authorization_scope,
            identity_context=context,
        )

    def _result(
        self,
        text,
        action=CommandAction.NONE,
        action_value=None,
        *,
        ignored=False,
    ):
        return DiscordDispatchResult(
            messages=split_discord_text(text, self.message_limit),
            action=action,
            action_value=action_value,
            ignored=ignored,
        )

    def process_message(
        self,
        content,
        *,
        user_id,
        guild_id=None,
        channel_id=None,
        is_bot=False,
    ):
        if is_bot:
            return DiscordDispatchResult(ignored=True)

        context = DiscordTrustContext.from_ids(
            user_id,
            guild_id,
            channel_id,
        )
        bind_discord_identity(self.trust_service, context)

        memory = self.memory_store.get(context.memory_scope)
        runtime = self._runtime_for(context)

        command_result = handle_command(content, memory, runtime)
        if command_result is not None:
            if command_result.action == CommandAction.EXIT_SESSION:
                self.memory_store.reset(context.memory_scope)

            return self._result(
                command_result.text,
                command_result.action,
                command_result.action_value,
            )

        response, should_exit = handle_message(content, memory)
        action = (
            CommandAction.EXIT_SESSION
            if should_exit
            else CommandAction.NONE
        )

        if should_exit:
            self.memory_store.reset(context.memory_scope)

        if response is None:
            return DiscordDispatchResult(action=action)

        return self._result(response, action)
