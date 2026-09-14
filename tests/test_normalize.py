import unittest
from difflib import SequenceMatcher

from data import argentine as ar
from data import english as en
from engine.normalize import fuzzy_match, normalize_message


class NormalizeOptimizationTests(unittest.TestCase):
    def test_normalization_contract_samples(self):
        cases = (
            ("", ""),
            (" hello ", "hello"),
            ("Heeey!!!", "hey"),
            ("what's up?", "whats up"),
            ("¿Cómo estás?", "cómo estás"),
            ("H000la!!!", "hola"),
            ("  multiple   spaces  ", "multiple spaces"),
            ("111", "l"),
        )
        for raw, expected in cases:
            with self.subTest(raw=raw):
                self.assertEqual(normalize_message(raw), expected)

    def test_fuzzy_match_matches_reference_for_detector_vocabularies(self):
        fuzzy_sets = (
            (en.ACTIVITY_RECALL, 0.90),
            (ar.ACTIVITY_RECALL, 0.90),
            (en.GREETING_WORDS, 0.88),
            (ar.GREETING_WORDS, 0.88),
        )

        texts = {
            "",
            "helo",
            "helllo",
            "quantum banana protocol",
            "what am i workin on",
            "que estaba haciend",
            "zzzzzzzz",
        }

        for candidates, _ in fuzzy_sets:
            for candidate in candidates:
                texts.add(candidate)
                if len(candidate) > 1:
                    for index in range(len(candidate)):
                        texts.add(
                            candidate[:index] + candidate[index + 1 :]
                        )
                texts.add(candidate + "x")
                texts.add("x" + candidate)

        for candidates, cutoff in fuzzy_sets:
            for text in sorted(texts):
                expected = any(
                    SequenceMatcher(None, text, candidate).ratio()
                    >= cutoff
                    for candidate in candidates
                )
                with self.subTest(
                    text=text,
                    cutoff=cutoff,
                    candidates=len(candidates),
                ):
                    self.assertEqual(
                        fuzzy_match(text, candidates, cutoff=cutoff),
                        expected,
                    )

    def test_fuzzy_match_keeps_close_typo(self):
        self.assertTrue(fuzzy_match("helo", {"hello"}))

    def test_fuzzy_match_rejects_far_input(self):
        self.assertFalse(
            fuzzy_match(
                "quantum banana protocol",
                en.GREETING_WORDS,
            )
        )


if __name__ == "__main__":
    unittest.main()
