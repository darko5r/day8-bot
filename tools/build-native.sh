#!/usr/bin/env bash
set -euo pipefail

repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cc="${CC:-gcc}"

mkdir -p "$repo/build"

"$cc" \
    -std=c17 \
    -O2 \
    -fPIC \
    -shared \
    -Wall \
    -Wextra \
    -Werror \
    -pedantic \
    "$repo/native/command_token.c" \
    -o "$repo/build/libdeedee_command_name.so"

printf 'Built %s\n' "$repo/build/libdeedee_command_name.so"
