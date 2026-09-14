import ctypes
import os
import re
from pathlib import Path


COMMAND_NAME_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9_-]*$")
EXPECTED_ABI_VERSION = 1


def normalize_command_token_python(token):
    if not COMMAND_NAME_PATTERN.fullmatch(token):
        return None
    return token.lower()


class NativeCommandToken:
    def __init__(self, library_path):
        self.library_path = Path(library_path)
        self._lib = ctypes.CDLL(str(self.library_path))

        self._lib.deedee_command_name_abi_version.argtypes = []
        self._lib.deedee_command_name_abi_version.restype = ctypes.c_int

        self._lib.deedee_command_name_normalize.argtypes = [
            ctypes.c_char_p,
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_char),
            ctypes.c_size_t,
        ]
        self._lib.deedee_command_name_normalize.restype = ctypes.c_int

        version = self._lib.deedee_command_name_abi_version()
        if version != EXPECTED_ABI_VERSION:
            raise RuntimeError(
                f"native command ABI mismatch: expected "
                f"{EXPECTED_ABI_VERSION}, got {version}"
            )

    def normalize(self, token):
        try:
            encoded = token.encode("ascii")
        except UnicodeEncodeError:
            return None

        output = ctypes.create_string_buffer(len(encoded) + 1)
        result = self._lib.deedee_command_name_normalize(
            encoded,
            len(encoded),
            output,
            len(output),
        )

        if result == 1:
            return output.value.decode("ascii")
        if result == 0:
            return None
        raise RuntimeError("native command normalizer returned an internal error")


def _default_library_path():
    override = os.environ.get("DEEDEE_NATIVE_CMD_LIB")
    if override:
        return Path(override)

    repository_root = Path(__file__).resolve().parents[2]
    return repository_root / "build" / "libdeedee_command_name.so"


def _load_default_native():
    path = _default_library_path()
    if not path.is_file():
        return None

    try:
        return NativeCommandToken(path)
    except (OSError, RuntimeError):
        return None


_DEFAULT_NATIVE = _load_default_native()


def backend_name():
    return "c" if _DEFAULT_NATIVE is not None else "python"


def normalize_command_token(token):
    if _DEFAULT_NATIVE is None:
        return normalize_command_token_python(token)
    return _DEFAULT_NATIVE.normalize(token)
