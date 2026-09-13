import random
import string

greetings = {
    "hi",
    "hello",
    "hey",
    "yo",
    "sup",
    "wassup",
    "wagwan",
    "hola",
    "holis",
}

greeting_responses = (
    "Dee Dee: Wah gwaan? U good?",
    "Dee Dee: Yo, mi deh yah. What’s good?",
    "Dee Dee: Holis, qué onda?",
    "Dee Dee: Ayy, what’s the vibe?",
)

exit_commands = {
    "bye",
    "goodbye",
    "exit",
    "quit",
    "chau",
    "chao",
}

goodbye_responses = (
    "Dee Dee: Aight, walk good.",
    "Dee Dee: Later then, stay easy.",
    "Dee Dee: Chauuu, nos vemos.",
)

unknown_responses = (
    "Dee Dee: Mi nah catch that one. Run it by me different.",
    "Dee Dee: Hold up, what you mean by that?",
    "Dee Dee: Nah, you lost me there. Say it another way.",
)

while True:
    user_message = input("U: ")

    normalized_message = user_message.lower().strip().translate(
        str.maketrans({"0": "o", "1": "l"})
    )

    normalized_message = normalized_message.translate(
        str.maketrans("", "", string.punctuation + "¿¡")
    )

    words = normalized_message.split()

    if normalized_message in exit_commands:
        print(random.choice(goodbye_responses))
        break

    greeting_phrase = (
        normalized_message.startswith("que onda")
        or normalized_message.startswith("qué onda")
    )

    if greetings.intersection(words) or greeting_phrase:
        print(random.choice(greeting_responses))
    else:
        print(random.choice(unknown_responses))
