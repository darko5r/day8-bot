GREETING_WORDS = {"hola", "holis", "buenas"}

GOODBYE_WORDS = {"chau", "chao"}

WELLBEING_QUESTIONS = {
    "como estas", "cómo estás", "como andas", "cómo andás", "todo bien",
    "todo tranqui", "todo piola", "como venis", "cómo venís",
}

WELLBEING_POSITIVE = {
    "si", "sí", "bien", "joya", "tranqui", "piola", "todo bien", "de diez",
    "re bien", "todo joya", "ando bien", "estoy bien",
}

WELLBEING_NEGATIVE = {
    "no", "mal", "medio mal", "para nada bien", "bastante mal", "muy mal",
    "hecho mierda", "estoy mal", "ando mal",
}

WELLBEING_NEUTRAL = {
    "mas o menos", "más o menos", "ahi", "ahí", "tirando", "meh",
    "ni bien ni mal", "vamos tirando",
}

VIBE_ANSWERS = {
    "laburando", "aca laburando", "acá laburando", "trabajando",
    "aca trabajando", "acá trabajando", "nada", "tranqui", "todo tranqui",
    "todo piola", "bien", "lo de siempre", "estudiando", "programando",
    "debuggeando", "probando cosas",
}

ACTIVITY_RECALL = {
    "en que estaba laburando", "en qué estaba laburando", "que estaba haciendo",
    "qué estaba haciendo", "en que andaba", "en qué andaba",
    "recordame en que estaba", "recordame en qué estaba",
}

MORE_RECALL = {
    "que mas", "qué más", "que mas estaba haciendo", "qué más estaba haciendo",
    "contame mas", "contame más", "en que estaba enfocado", "en qué estaba enfocado",
}

NEXT_RECALL = {
    "que sigue", "qué sigue", "que hago despues", "qué hago después",
    "que deberia hacer despues", "qué debería hacer después",
    "que me sugeris hacer despues", "qué me sugerís hacer después",
    "cual es el proximo paso", "cuál es el próximo paso",
}

NAME_RECALL = {
    "como me llamo", "cómo me llamo", "cual es mi nombre", "cuál es mi nombre",
    "te acordas mi nombre", "te acordás mi nombre", "quien soy", "quién soy",
}

MARKERS = {
    "hola", "holis", "buenas", "como", "cómo", "estas", "estás", "andas",
    "andás", "vos", "che", "bien", "gracias", "dale", "chau", "chao",
    "onda", "tranqui", "piola", "posta", "joya", "laburando", "mal",
}

GREETING_OPTIONS = (
    ("Dee Dee: Che, ¿qué onda?", "vibe"),
    ("Dee Dee: Holis, ¿todo piola?", "wellbeing"),
    ("Dee Dee: Buenas, ¿todo tranqui?", "wellbeing"),
    ("Dee Dee: De una, acá estoy. ¿Qué contás?", "vibe"),
)

GOODBYE_RESPONSES = (
    "Dee Dee: Dale, nos vemos.",
    "Dee Dee: De una, chau. Que andes bien.",
    "Dee Dee: Chauuu, nos vemos después.",
)

WELLBEING_RESPONSES = (
    "Dee Dee: Todo piola por acá. ¿Y vos?",
    "Dee Dee: Acá, tranqui. ¿Vos cómo venís?",
    "Dee Dee: De diez. ¿Y vos, todo bien?",
    "Dee Dee: Todo joya. ¿Qué onda vos?",
)

POSITIVE_FOLLOWUPS = (
    "Dee Dee: De una, me alegro. ¿Qué hacés hoy?",
    "Dee Dee: Joya entonces. ¿En qué andás?",
    "Dee Dee: Bien ahí, che. ¿Cómo viene tu día?",
)

NEGATIVE_FOLLOWUPS = (
    "Dee Dee: Uh, qué bajón. ¿Querés contarme qué pasó?",
    "Dee Dee: Che, te escucho. ¿Qué te tiene así?",
    "Dee Dee: Bueno, sin chamuyo. ¿Qué anda mal?",
)

NEUTRAL_FOLLOWUPS = (
    "Dee Dee: Y... más o menos entonces. ¿Qué anda pasando?",
    "Dee Dee: Te entiendo. Ni fu ni fa. ¿Qué tenés en la cabeza?",
    "Dee Dee: Bueno, ahí vamos. ¿Qué onda, qué pasó?",
)

WELLBEING_DETAIL_ACK = (
    "Dee Dee: Te entiendo, che. Gracias por contármelo de frente.",
    "Dee Dee: Dale, te sigo.",
    "Dee Dee: Sí, te entiendo. Quedó claro.",
)

VIBE_FOLLOWUPS = (
    "Dee Dee: De una. ¿En qué estás laburando concretamente?",
    "Dee Dee: Piola. ¿Qué proyecto tenés entre manos?",
    "Dee Dee: Joya. ¿Qué estás armando o resolviendo?",
)

ACTIVITY_DETAIL_PROMPTS = (
    "Dee Dee: De una. ¿Qué parte te tiene más ocupado?",
    "Dee Dee: Piola. ¿Qué es lo que más te está costando?",
    "Dee Dee: Joya. ¿Qué estás tratando de resolver ahí?",
)

NEXT_STEP_PROMPTS = (
    "Dee Dee: Te sigo. ¿Cuál sería el próximo paso?",
    "Dee Dee: De una. ¿Qué pensás hacer después?",
    "Dee Dee: Joya. ¿Y ahora qué sigue?",
)

COMPLETION_RESPONSES = (
    "Dee Dee: De una, ahora sí tengo el panorama.",
    "Dee Dee: Joya, ahí quedó claro.",
    "Dee Dee: Bien ahí, ahora entiendo por dónde viene.",
)

UNKNOWN_RESPONSES = (
    "Dee Dee: Che, ahí me mataste. Decímelo de otra forma.",
    "Dee Dee: Esa no la cacé. Tirámela de otra manera.",
    "Dee Dee: Bancá, ahí me perdí. Explicámelo distinto.",
    "Dee Dee: Posta que no agarré esa. Probá de nuevo.",
)

# Challenge-completeness FAQ, fun, and adaptive-personality vocabulary.
BOT_IDENTITY_QUESTIONS = {
    "quien sos", "quién sos", "que sos", "qué sos", "que es dee dee",
    "qué es dee dee", "contame quien sos", "contame quién sos",
}

BOT_CAPABILITIES_QUESTIONS = {
    "que podes hacer", "qué podés hacer", "que haces", "qué hacés",
    "en que me podes ayudar", "en qué me podés ayudar",
    "como me podes ayudar", "cómo me podés ayudar",
}

JOKE_REQUESTS = {
    "contame un chiste", "tirate un chiste", "tírate un chiste",
    "haceme reir", "haceme reír", "decime algo gracioso",
}

DISCOURAGEMENT_PHRASES = {
    "me rindo", "no puedo con esto", "no me sale", "soy un desastre",
    "no lo voy a sacar", "ya fue no puedo", "fallo cinco veces",
    "falló cinco veces",
}

ENGINEERING_ANTIPATTERN_PHRASES = {
    "borre el test", "borré el test", "saque el test", "saqué el test",
    "desactive el test", "desactivé el test", "ignore el error",
    "ignoré el error",
}

TECHNICAL_SETBACK_PHRASES = {
    "fallo otra vez", "falló otra vez", "sigue fallando", "todavia falla",
    "todavía falla", "no anda", "sigue roto", "mismo error", "otro error",
}

TECHNICAL_SUCCESS_PHRASES = {
    "funciona ahora", "ya funciona", "ya anda", "lo arregle", "lo arreglé",
    "pasaron los tests", "los tests pasan", "anda ahora",
}

BOT_IDENTITY_RESPONSES = (
    "Dee Dee: Soy Dee Dee: revisora técnica, mentora, ayudante de proyectos "
    "y medio servicio de red old-school. Estricta con la evidencia, seca con "
    "el sarcasmo y con criterio para saber cuándo cortar el chiste.",
    "Dee Dee: Dee Dee. Revisión técnica, mentoría, ayuda de proyecto y alma "
    "de servicio viejo. Me gusta la evidencia y tengo poca paciencia para "
    "las decisiones de ingeniería que se merecen una gastada.",
)

BOT_CAPABILITIES_RESPONSES = (
    "Dee Dee: Puedo charlar, recordar tu nombre y el contexto de tu tarea, "
    "contestar preguntas comunes, tirar chistes y manejar mi sistema de "
    "comandos y confianza. Poné !help para ver el registro.",
    "Dee Dee: Conversación, memoria de tareas, preguntas comunes, humor, tono "
    "adaptativo y comandos propios. !help te muestra el lado de servicio.",
)

JOKES = (
    "Dee Dee: Un dev dijo 'en mi máquina anda'. "
    "El servidor respondió: 'mirá qué suerte la tuya'.",
    "Dee Dee: Le pedí al bug pasos para reproducirse. "
    "Me contestó: 'deployá un viernes'.",
    "Dee Dee: Borraron el test que fallaba. Impecable: "
    "ahora el bug viene con menos documentación.",
    "Dee Dee: El código tenía una sola tarea. Se la delegó a comportamiento indefinido.",
)

SARCASTIC_ENGINEERING_RESPONSES = (
    "Dee Dee: Hermoso. Si borramos el test, el test deja de fallar. "
    "Volvelo a poner y arreglemos el problema de verdad.",
    "Dee Dee: Tremenda estrategia: silenciar la evidencia y declarar victoria. "
    "No. Revertí eso y mostrame el fallo.",
    "Dee Dee: Ah, sí, la técnica ancestral de sacar la alarma porque hace ruido. "
    "Deshacelo y vamos al error real.",
)

FOCUSED_SETBACK_RESPONSES = (
    "Dee Dee: Bien. Un fallo es un dato, no una sentencia. "
    "Mostrame el primer paso que da distinto de lo esperado.",
    "Dee Dee: Sin adivinar todavía. Pasame la salida exacta y dónde aparece "
    "la primera divergencia.",
)

MOTIVATIONAL_RESPONSES = (
    "Dee Dee: No. El proyecto no va a la basura por insistente. "
    "Cada fallo es evidencia. Mostrame la primera divergencia y seguimos desde ahí.",
    "Dee Dee: Seguís acá, así que seguimos laburando. "
    "No cuentes fallos como derrotas; contá qué hipótesis descartó cada uno.",
    "Dee Dee: Esto no te gana por repetición. Salida exacta, expectativa exacta, "
    "primera diferencia. Una cosa por vez.",
)

PLAYFUL_SUCCESS_RESPONSES = (
    "Dee Dee: Mirá vos, la máquina dejó de discutir. Bien. "
    "Ahora verificá la regresión antes de hacer la vuelta olímpica.",
    "Dee Dee: Después de todo el drama decidió andar. Perfecto. "
    "Probalo dos veces y recién ahí le creemos.",
    "Dee Dee: Ahí está. Victoria provisoria: tests primero, festejo después.",
)

