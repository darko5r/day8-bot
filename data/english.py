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
