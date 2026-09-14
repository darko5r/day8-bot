import time

from engine.commands.models import CommandAction, CommandRuntime
from engine.commands.service import handle_command
from engine.conversation import handle_message
from engine.memory import MemoryStore


TERMINAL_SCOPE = ("terminal", "terminal", "user")


def main():
    store = MemoryStore()
    memory = store.get(TERMINAL_SCOPE)
    runtime = CommandRuntime(
        started_at=time.monotonic(),
        clock=time.monotonic,
        protocol="terminal",
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
            if command_result.action == CommandAction.EXIT_SESSION:
                break
            continue

        response, should_exit = handle_message(user_message, memory)
        print(response)

        if should_exit:
            break


if __name__ == "__main__":
    main()
