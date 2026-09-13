import random
import string

user_message = input("U: ")

normalized_message = user_message.lower().strip().translate(
    str.maketrans({"0": "o", "1": "l"})
)

normalized_message = normalized_message.translate(
    str.maketrans("", "", string.punctuation + "¿¡")
)

words = normalized_message.split()

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

greeting_phrase = (
    normalized_message.startswith("que onda")
    or normalized_message.startswith("qué onda")
)

greeting_responses = (
    "Dee Dee: Wah gwaan? U good?",
    "Dee Dee: Yo, mi deh yah. What’s good?",
    "Dee Dee: Holis 😏 qué onda?",
    "Dee Dee: Ayy, what’s the vibe?",
)

if greetings.intersection(words) or greeting_phrase:
    print(random.choice(greeting_responses))
