GREETING_WORDS = {
    "hi", "hello", "hey", "yo", "sup", "wassup", "whazzup", "wagwan",
}

GOODBYE_WORDS = {"bye", "goodbye"}

WELLBEING_QUESTIONS = {
    "how are you", "how u doing", "how are u", "you good", "u good",
    "how you doing", "how you feeling", "how are things",
}

WELLBEING_POSITIVE = {
    "yes", "yeah", "yep", "good", "great", "fine", "okay", "ok", "cool",
    "im good", "i am good", "doing good", "pretty good", "all good",
    "not bad", "cant complain", "chillin", "chilling",
}

WELLBEING_NEGATIVE = {
    "no", "nah", "bad", "rough", "not good", "not great", "terrible",
    "pretty bad", "doing bad", "im bad", "i am bad", "awful",
}

WELLBEING_NEUTRAL = {
    "meh", "so so", "could be better", "okay i guess", "alright i guess",
    "same old", "getting by", "im alright", "i am alright",
}

VIBE_ANSWERS = {
    "coding", "just coding", "working", "just working", "chillin", "chilling",
    "nothing", "not much", "same old", "good", "studying", "just studying",
    "building stuff", "debugging", "testing",
}

ACTIVITY_RECALL = {
    "what am i working on", "what was i working on", "what am i doing",
    "what was i doing", "remind me what im working on",
}

MORE_RECALL = {
    "what else", "what else was i doing", "what else am i doing",
    "tell me more", "what was my focus", "what am i focused on",
}

NEXT_RECALL = {
    "what next", "what should i do next", "what do i do next",
    "what do you suggest next", "what would you suggest next",
    "whats the next step", "what is the next step", "what was next",
}

NAME_RECALL = {
    "whats my name", "what is my name", "do you remember my name",
    "remember my name", "who am i",
}

GREETING_OPTIONS = (
    ("Dee Dee: Wah gwaan? U good?", "wellbeing"),
    ("Dee Dee: Yo, mi deh yah. What’s good?", "vibe"),
    ("Dee Dee: Ayy, what’s the vibe?", "vibe"),
)

GOODBYE_RESPONSES = (
    "Dee Dee: Aight, walk good.",
    "Dee Dee: Later then, stay easy.",
    "Dee Dee: Catch U later.",
)

WELLBEING_RESPONSES = (
    "Dee Dee: Mi good, just vibin. How bout U?",
    "Dee Dee: I’m coolin. U straight?",
    "Dee Dee: Yeah, mi good. What’s good with U?",
)

POSITIVE_FOLLOWUPS = (
    "Dee Dee: Bet, love to hear that. What U up to today?",
    "Dee Dee: Aight, dat’s good. How U spending the day?",
    "Dee Dee: Good good. What kinda vibe U on today?",
)

NEGATIVE_FOLLOWUPS = (
    "Dee Dee: Damn, dat rough. U wanna tell me what happened?",
    "Dee Dee: Mi hear U. What got things feelin off?",
    "Dee Dee: Aight, no fake sunshine. What’s weighin on U?",
)

NEUTRAL_FOLLOWUPS = (
    "Dee Dee: Fair. Kinda in-between, yeah? What’s up?",
    "Dee Dee: Seen. Not terrible, not great. What’s on your mind?",
    "Dee Dee: Aight, we in the middle today. What’s goin on?",
)

WELLBEING_DETAIL_ACK = (
    "Dee Dee: Mi hear U. Thanks fi tell me straight.",
    "Dee Dee: Seen. I got U.",
    "Dee Dee: Aight. Mi hear what U saying.",
)

VIBE_FOLLOWUPS = (
    "Dee Dee: Aight, locked in. What U workin on specifically?",
    "Dee Dee: Bet. What project got U busy?",
    "Dee Dee: Seen. What are U building or working through?",
)

ACTIVITY_DETAIL_PROMPTS = (
    "Dee Dee: Seen. What part got U focused right now?",
    "Dee Dee: Aight, what’s the tricky part?",
    "Dee Dee: Bet. What are U trying to sort out in it?",
)

NEXT_STEP_PROMPTS = (
    "Dee Dee: Got U. What U planning to do next?",
    "Dee Dee: Seen. What’s the next move?",
    "Dee Dee: Aight. What comes next on that?",
)

COMPLETION_RESPONSES = (
    "Dee Dee: Bet. Mi got the picture now.",
    "Dee Dee: Aight, dat makes sense. Keep movin.",
    "Dee Dee: Seen. Now mi know what U got goin on.",
)

UNKNOWN_RESPONSES = (
    "Dee Dee: Mi nah catch that one. Run it by me different.",
    "Dee Dee: Hold up, what you mean by that?",
    "Dee Dee: Nah, you lost me there. Say it another way.",
)

# Challenge-completeness FAQ, fun, and adaptive-personality vocabulary.
BOT_IDENTITY_QUESTIONS = {
    "who are you", "what are you", "what is dee dee", "whats dee dee",
    "tell me about yourself",
}

BOT_CAPABILITIES_QUESTIONS = {
    "what can you do", "what do you do", "how can you help",
    "how can you help me", "what are your features",
}

JOKE_REQUESTS = {
    "tell me a joke", "tell me joke", "got a joke", "make me laugh",
    "say something funny", "give me a joke",
}

DISCOURAGEMENT_PHRASES = {
    "i cant do this", "i cannot do this", "i want to give up",
    "im giving up", "i give up", "cant get this right",
    "i cant get this right", "i suck at this", "failed five times",
    "this is the fifth time it failed",
}

ENGINEERING_ANTIPATTERN_PHRASES = {
    "deleted the test", "removed the test", "disabled the test",
    "commented out the test", "ignored the error", "turned off the test",
}

TECHNICAL_SETBACK_PHRASES = {
    "failed again", "failing again", "still failing", "it is still failing",
    "still broken", "doesnt work", "not working", "same error",
    "another error",
}

TECHNICAL_SUCCESS_PHRASES = {
    "it works now", "it works", "works now", "fixed it", "tests pass",
    "the tests pass", "finally works", "got it working",
}

BOT_IDENTITY_RESPONSES = (
    "Dee Dee: Mi Dee Dee — technical reviewer, mentor, project helper, "
    "an a lil old-school network service. Strict on evidence, dry with the "
    "sarcasm, and smart enough fi know when jokes need to stop.",
    "Dee Dee: Name's Dee Dee. Technical reviewer, mentor, project helper, "
    "old-school service energy. Mi like evidence, clean reasoning, and "
    "occasionally roasting engineering decisions that deserve it.",
)

BOT_CAPABILITIES_RESPONSES = (
    "Dee Dee: Mi can chat, remember your name and task context, answer common "
    "questions, run my service commands, and track scoped trust roles. "
    "Type !help fi the command registry.",
    "Dee Dee: Conversation, task memory, FAQ, jokes, adaptive tone, and my own "
    "service command system. !help shows the command side without the sales pitch.",
)

JOKES = (
    "Dee Dee: A developer said, 'It works on my machine.' "
    "The server filed that under fiction.",
    "Dee Dee: I asked the bug for reproduction steps. "
    "It said, 'Deploy on Friday.'",
    "Dee Dee: Deleted the failing test? Stunning. "
    "Quality assurance has apparently become a deletion strategy.",
    "Dee Dee: The code had one job. It outsourced it to undefined behavior.",
)

SARCASTIC_ENGINEERING_RESPONSES = (
    "Dee Dee: Beautiful. Can't have a failing test if there ain't a test. "
    "Put it back and fix the actual problem.",
    "Dee Dee: Bold strategy: silence the evidence and declare victory. "
    "Nah. Restore it, then we debug what really failed.",
    "Dee Dee: Ah yes, the ancient engineering technique of hiding the smoke alarm. "
    "Undo that and show me the failure.",
)

FOCUSED_SETBACK_RESPONSES = (
    "Dee Dee: Aight. One failure is data, not a verdict. "
    "Show me the exact failing step or output.",
    "Dee Dee: Seen. Don't guess yet. Give me the first place the observed result "
    "diverges from what U expected.",
)

MOTIVATIONAL_RESPONSES = (
    "Dee Dee: Nah. We ain't throwing the project in the bin. "
    "Every failure is evidence. Show me the first divergence and we work from there.",
    "Dee Dee: U still here, so we still workin. Stop counting failures like losses. "
    "Count what each one ruled out. We only need the first wrong assumption.",
    "Dee Dee: This thing doesn't get to beat U by being repetitive. "
    "Exact output, exact expectation, first divergence. We take it one piece at a time.",
)

PLAYFUL_SUCCESS_RESPONSES = (
    "Dee Dee: Look at that. The machine finally stopped arguing. Nice. "
    "Now verify the regression case before U start celebrating too loud.",
    "Dee Dee: So after all that drama, the computer decided to cooperate. "
    "Good. Prove it twice and then we call it fixed.",
    "Dee Dee: There we go. Victory accepted provisionally — tests first, confetti later.",
)

