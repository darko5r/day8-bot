import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from engine.native.command_token import (
    NativeCommandToken,
    normalize_command_token,
    normalize_command_token_python,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


class NativeCommandTokenTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        compiler = shutil.which("gcc")
        if compiler is None:
            raise unittest.SkipTest("gcc is unavailable")

        cls.tempdir = tempfile.TemporaryDirectory()
        cls.library_path = Path(cls.tempdir.name) / "libdeedee_command_name.so"
        subprocess.run(
            [
                compiler,
                "-std=c17",
                "-O2",
                "-fPIC",
                "-shared",
                "-Wall",
                "-Wextra",
                "-Werror",
                "-pedantic",
                str(REPOSITORY_ROOT / "native" / "command_token.c"),
                "-o",
                str(cls.library_path),
            ],
            check=True,
        )
        cls.native = NativeCommandToken(cls.library_path)

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "tempdir"):
            cls.tempdir.cleanup()

    def test_python_fallback_normalizes_valid_names(self):
        for raw, expected in (
            ("help", "help"),
            ("HELP", "help"),
            ("Who-Is", "who-is"),
            ("a_1", "a_1"),
        ):
            with self.subTest(raw=raw):
                self.assertEqual(
                    normalize_command_token_python(raw),
                    expected,
                )

    def test_python_fallback_rejects_invalid_names(self):
        for raw in ("", "1help", "a.b", "help!", "ümlaut"):
            with self.subTest(raw=raw):
                self.assertIsNone(normalize_command_token_python(raw))

    def test_native_abi_loads(self):
        self.assertEqual(self.native.normalize("help"), "help")

    def test_native_normalizes_valid_names(self):
        for raw, expected in (
            ("help", "help"),
            ("HELP", "help"),
            ("Who-Is", "who-is"),
            ("a_1", "a_1"),
        ):
            with self.subTest(raw=raw):
                self.assertEqual(self.native.normalize(raw), expected)

    def test_native_rejects_invalid_names(self):
        for raw in ("", "1help", "a.b", "help!", "ümlaut"):
            with self.subTest(raw=raw):
                self.assertIsNone(self.native.normalize(raw))

    def test_native_and_python_are_equivalent_on_corpus(self):
        corpus = (
            "help",
            "HELP",
            "Help",
            "whois",
            "WHOIS",
            "a",
            "a1",
            "a_1",
            "a-b",
            "",
            "1a",
            "_a",
            "-a",
            "a.b",
            "a/b",
            "a b",
            "ümlaut",
        )
        for raw in corpus:
            with self.subTest(raw=raw):
                self.assertEqual(
                    self.native.normalize(raw),
                    normalize_command_token_python(raw),
                )

    def test_native_preserves_only_ascii_contract(self):
        self.assertIsNone(self.native.normalize("héLp"))
        self.assertIsNone(normalize_command_token_python("héLp"))

    def test_default_helper_matches_python_contract(self):
        corpus = ("help", "HELP", "a_1", "a-b", "1bad", "bad.name")
        for raw in corpus:
            with self.subTest(raw=raw):
                self.assertEqual(
                    normalize_command_token(raw),
                    normalize_command_token_python(raw),
                )

    def test_fresh_process_can_select_native_library(self):
        code = (
            "from engine.native.command_token import backend_name, "
            "normalize_command_token; "
            "assert backend_name() == 'c'; "
            "assert normalize_command_token('HeLp') == 'help'; "
            "assert normalize_command_token('1help') is None"
        )
        env = os.environ.copy()
        env["PYTHONPATH"] = str(REPOSITORY_ROOT)
        env["DEEDEE_NATIVE_CMD_LIB"] = str(self.library_path)
        subprocess.run(
            [sys.executable, "-c", code],
            check=True,
            env=env,
            cwd=REPOSITORY_ROOT,
        )

    def test_fresh_process_falls_back_when_library_is_missing(self):
        code = (
            "from engine.native.command_token import backend_name, "
            "normalize_command_token; "
            "assert backend_name() == 'python'; "
            "assert normalize_command_token('HeLp') == 'help'; "
            "assert normalize_command_token('1help') is None"
        )
        env = os.environ.copy()
        env["PYTHONPATH"] = str(REPOSITORY_ROOT)
        env["DEEDEE_NATIVE_CMD_LIB"] = str(
            Path(self.tempdir.name) / "missing.so"
        )
        subprocess.run(
            [sys.executable, "-c", code],
            check=True,
            env=env,
            cwd=REPOSITORY_ROOT,
        )


if __name__ == "__main__":
    unittest.main()
