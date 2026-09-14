#include "command_token.h"

static int ascii_alpha(unsigned char ch) {
    return ((ch >= (unsigned char)'A' && ch <= (unsigned char)'Z') ||
            (ch >= (unsigned char)'a' && ch <= (unsigned char)'z'));
}

static int ascii_digit(unsigned char ch) {
    return ch >= (unsigned char)'0' && ch <= (unsigned char)'9';
}

static unsigned char ascii_lower(unsigned char ch) {
    if (ch >= (unsigned char)'A' && ch <= (unsigned char)'Z') {
        return (unsigned char)(ch + ((unsigned char)'a' - (unsigned char)'A'));
    }
    return ch;
}

int deedee_command_name_abi_version(void) {
    return DEEDEE_COMMAND_NAME_ABI_VERSION;
}

int deedee_command_name_normalize(
    const char *input,
    size_t input_len,
    char *output,
    size_t output_cap
) {
    size_t i;

    if (input == NULL || output == NULL) {
        return -1;
    }

    if (input_len == 0U) {
        return 0;
    }

    if (output_cap <= input_len) {
        return -1;
    }

    if (!ascii_alpha((unsigned char)input[0])) {
        return 0;
    }

    for (i = 0U; i < input_len; ++i) {
        unsigned char ch = (unsigned char)input[i];

        if (!(ascii_alpha(ch) ||
              ascii_digit(ch) ||
              ch == (unsigned char)'_' ||
              ch == (unsigned char)'-')) {
            return 0;
        }

        output[i] = (char)ascii_lower(ch);
    }

    output[input_len] = '\0';
    return 1;
}
