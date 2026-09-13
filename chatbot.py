import random
import string

english_greetings = {
    "hi",
    "hello",
    "hey",
    "yo",
    "sup",
    "wassup",
    "wagwan",
}

argentine_greetings = {
    "hola",
    "holis",
}

english_greeting_options = (
    (
        "Dee Dee: Wah gwaan? U good?",
        "waiting_for_english_wellbeing",
    ),
    (
        "Dee Dee: Yo, mi deh yah. What’s good?",
        "waiting_for_english_vibe",
    ),
    (
        "Dee Dee: Ayy, what’s the vibe?",
        "waiting_for_english_vibe",
    ),
)

argentine_greeting_options = (
    (
        "Dee Dee: Che, ¿qué onda?",
        "waiting_for_argentine_vibe",
    ),
    (
        "Dee Dee: Holis, ¿todo piola?",
        "waiting_for_argentine_wellbeing",
    ),
    (
        "Dee Dee: Buenas, ¿todo tranqui?",
        "waiting_for_argentine_wellbeing",
    ),
    (
        "Dee Dee: De una, acá estoy. ¿Qué contás?",
        "waiting_for_argentine_vibe",
    ),
)

english_exit_commands = {
    "bye",
    "goodbye",
    "exit",
    "quit",
}

argentine_exit_commands = {
    "chau",
    "chao",
}

english_goodbye_responses = (
    "Dee Dee: Aight, walk good.",
    "Dee Dee: Later then, stay easy.",
    "Dee Dee: Catch U later.",
)

argentine_goodbye_responses = (
    "Dee Dee: Dale, nos vemos.",
    "Dee Dee: De una, chau. Que andes bien.",
    "Dee Dee: Chauuu, nos vemos después.",
)

english_wellbeing_questions = {
    "how are you",
    "how u doing",
    "you good",
}

argentine_wellbeing_questions = {
    "como estas",
    "cómo estás",
    "como andas",
    "cómo andás",
    "todo bien",
    "todo tranqui",
    "todo piola",
}

english_wellbeing_responses = (
    "Dee Dee: Mi good, just vibin. How bout U?",
    "Dee Dee: I’m coolin. U straight?",
    "Dee Dee: Yeah, mi good. What’s good with U?",
)

argentine_wellbeing_responses = (
    "Dee Dee: Todo piola por acá. ¿Y vos?",
    "Dee Dee: Acá, tranqui. ¿Vos cómo venís?",
    "Dee Dee: De diez. ¿Y vos, todo bien?",
    "Dee Dee: Todo joya. ¿Qué onda vos?",
)

english_positive_wellbeing = {
    "good",
    "great",
    "fine",
    "okay",
    "ok",
    "cool",
    "chillin",
    "chilling",
    "yes",
    "yeah",
    "yep",
}

argentine_positive_wellbeing = {
    "bien",
    "joya",
    "tranqui",
    "piola",
    "todo bien",
    "de diez",
    "si",
    "sí",
}

english_positive_followups = (
    "Dee Dee: Bet, love to hear that.",
    "Dee Dee: Aight, dat’s what mi like fi hear.",
    "Dee Dee: Good good, keep that energy.",
)

argentine_positive_followups = (
    "Dee Dee: De una, me alegro.",
    "Dee Dee: Joya entonces.",
    "Dee Dee: Bien ahí, che.",
)

english_vibe_answers = {
    "coding",
    "just coding",
    "working",
    "just working",
    "chillin",
    "chilling",
    "nothing",
    "not much",
    "same old",
    "good",
}

argentine_vibe_answers = {
    "laburando",
    "aca laburando",
    "acá laburando",
    "trabajando",
    "aca trabajando",
    "acá trabajando",
    "nada",
    "tranqui",
    "todo tranqui",
    "todo piola",
    "bien",
    "lo de siempre",
}

english_vibe_followups = (
    "Dee Dee: Aight, locked in. What U workin on?",
    "Dee Dee: Bet. What got U busy right now?",
    "Dee Dee: Seen. What U got goin on?",
)

argentine_vibe_followups = (
    "Dee Dee: De una. ¿En qué andás laburando?",
    "Dee Dee: Piola. ¿Qué tenés entre manos?",
    "Dee Dee: Joya. ¿En qué andás ahora?",
)

english_activity_responses = (
    "Dee Dee: Seen. Dat sound like a proper mission.",
    "Dee Dee: Aight, I see U cookin.",
    "Dee Dee: Bet. Keep pushin on that.",
)

argentine_activity_responses = (
    "Dee Dee: De una, suena piola eso.",
    "Dee Dee: Bien ahí, metele.",
    "Dee Dee: Joya, banco ese laburo.",
)

english_unknown_responses = (
    "Dee Dee: Mi nah catch that one. Run it by me different.",
    "Dee Dee: Hold up, what you mean by that?",
    "Dee Dee: Nah, you lost me there. Say it another way.",
)

argentine_unknown_responses = (
    "Dee Dee: Che, ahí me mataste. Decímelo de otra forma.",
    "Dee Dee: Esa no la cacé. Tirámela de otra manera.",
    "Dee Dee: Bancá, ahí me perdí. Explicámelo distinto.",
    "Dee Dee: Posta que no agarré esa. Probá de nuevo.",
)

argentine_markers = {
    "hola",
    "holis",
    "como",
    "cómo",
    "estas",
    "estás",
    "andas",
    "andás",
    "vos",
    "che",
    "bien",
    "gracias",
    "dale",
    "chau",
    "chao",
    "onda",
    "tranqui",
    "piola",
    "posta",
    "joya",
    "laburando",
}

conversation_state = None
last_activity = None

while True:
    user_message = input("U: ")

    normalized_message = user_message.lower().strip().translate(
        str.maketrans({"0": "o", "1": "l"})
    )

    normalized_message = normalized_message.translate(
        str.maketrans("", "", string.punctuation + "¿¡")
    )

    words = normalized_message.split()

    if normalized_message in english_exit_commands:
        print(random.choice(english_goodbye_responses))
        break

    if normalized_message in argentine_exit_commands:
        print(random.choice(argentine_goodbye_responses))
        break

    if (
        conversation_state == "waiting_for_english_wellbeing"
        and normalized_message in english_positive_wellbeing
    ):
        print(random.choice(english_positive_followups))
        conversation_state = None
        continue

    if (
        conversation_state == "waiting_for_argentine_wellbeing"
        and normalized_message in argentine_positive_wellbeing
    ):
        print(random.choice(argentine_positive_followups))
        conversation_state = None
        continue

    if (
        conversation_state == "waiting_for_english_vibe"
        and normalized_message in english_vibe_answers
    ):
        print(random.choice(english_vibe_followups))
        conversation_state = "waiting_for_english_activity"
        continue

    if (
        conversation_state == "waiting_for_argentine_vibe"
        and normalized_message in argentine_vibe_answers
    ):
        print(random.choice(argentine_vibe_followups))
        conversation_state = "waiting_for_argentine_activity"
        continue

    if conversation_state == "waiting_for_english_activity":
        last_activity = user_message.strip()

        print(random.choice(english_activity_responses))

        conversation_state = None
        continue

    if conversation_state == "waiting_for_argentine_activity":
        last_activity = user_message.strip()

        print(random.choice(argentine_activity_responses))

        conversation_state = None
        continue

    argentine_greeting_phrase = (
        normalized_message.startswith("que onda")
        or normalized_message.startswith("qué onda")
    )

    english_wellbeing_detected = any(
        phrase in normalized_message
        for phrase in english_wellbeing_questions
    )

    argentine_wellbeing_detected = any(
        phrase in normalized_message
        for phrase in argentine_wellbeing_questions
    )

    argentine_detected = (
        bool(argentine_markers.intersection(words))
        or argentine_greeting_phrase
        or argentine_wellbeing_detected
    )

    if argentine_wellbeing_detected:
        print(random.choice(argentine_wellbeing_responses))
        conversation_state = "waiting_for_argentine_wellbeing"

    elif english_wellbeing_detected:
        print(random.choice(english_wellbeing_responses))
        conversation_state = "waiting_for_english_wellbeing"

    elif argentine_greetings.intersection(words) or argentine_greeting_phrase:
        response, next_state = random.choice(argentine_greeting_options)

        print(response)
        conversation_state = next_state

    elif english_greetings.intersection(words):
        response, next_state = random.choice(english_greeting_options)

        print(response)
        conversation_state = next_state

    elif argentine_detected:
        print(random.choice(argentine_unknown_responses))

    else:
        print(random.choice(english_unknown_responses))
