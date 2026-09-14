from engine.conversation import handle_message
from engine.memory import MemoryStore


TERMINAL_SCOPE = ("terminal", "terminal", "user")


def main():
    store = MemoryStore()
    memory = store.get(TERMINAL_SCOPE)

    while True:
        user_message = input("U: ")
        response, should_exit = handle_message(user_message, memory)
        print(response)

        if should_exit:
            break


if __name__ == "__main__":
    main()
