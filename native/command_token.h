#ifndef DEEDEE_COMMAND_NAME_H
#define DEEDEE_COMMAND_NAME_H

#include <stddef.h>

#define DEEDEE_COMMAND_NAME_ABI_VERSION 1

int deedee_command_name_abi_version(void);

int deedee_command_name_normalize(
    const char *input,
    size_t input_len,
    char *output,
    size_t output_cap
);

#endif
