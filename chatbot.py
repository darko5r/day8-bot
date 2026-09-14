import time

from engine.commands.models import CommandAction, CommandRuntime
from engine.commands.service import handle_command
from engine.conversation import handle_message
from engine.memory import MemoryStore
from engine.trust.models import ScopeRef
from engine.trust.service import TrustService


TERMINAL_SCOPE = ("terminal", "terminal", "user")
TERMINAL_IDENTITY = "terminal:user"


def main():
    store = MemoryStore()
    memory = store.get(TERMINAL_SCOPE)
    trust = TrustService(founder_id=TERMINAL_IDENTITY)
    runtime = CommandRuntime(
        started_at=time.monotonic(),
        clock=time.monotonic,
        protocol="terminal",
        actor_id=TERMINAL_IDENTITY,
        trust_service=trust,
        authorization_scope=ScopeRef.global_scope(),
    )

    while True:
        user_message = input("U: ")

        command_result = handle_command(
            user_message,
            memory,
            runtime,
        )

        if command_result is not None:
            print(command_result.text)
            if command_result.action in {
                CommandAction.EXIT_SESSION,
                CommandAction.SHUTDOWN_SERVICE,
            }:
                break
            continue

        response, should_exit = handle_message(user_message, memory)
        if response is not None:
            print(response)

        if should_exit:
            break


if __name__ == "__main__":
    main()
