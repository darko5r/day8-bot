user_message = input("U: ")

normalized_message = user_message.lower().strip().translate(
    str.maketrans({"0": "o", "1": "l"})
)

words = normalized_message.split()

if "hi" in words or "hello" in words or "yo" in words:
    print("Dee Dee: Wah gwaan? U good?")
