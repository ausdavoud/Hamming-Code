import math


# def print_blocks(
#     encoded_blocks: list[list[int]],
#     old_blocks: list[list[int]] = None,
# ):
#     RESET = "\033[0m"
#     BLUE = "\033[94m"
#     GREEN = "\033[32m"
#     RED = "\033[91m"

#     parity_positions = [
#         2**i - 1 for i in range(int(math.log2(len(encoded_blocks[0]) + 1)))
#     ]
#     old_code = (
#         "".join("".join(map(str, block)) for block in old_blocks)
#         if old_blocks
#         else None
#     )
#     new_code = "".join("".join(map(str, block)) for block in encoded_blocks)

#     code = ""
#     for i in range(len(new_code)):
#         if i % len(encoded_blocks[0]) == 0 and i != 0:
#             code += " "
#         if old_blocks:
#             # Highlight differences if old_blocks is provided
#             if old_code[i] == new_code[i]:
#                 code += f"{GREEN}{new_code[i]}{RESET}"
#             else:
#                 code += f"{RED}{new_code[i]}{RESET}"
#         else:
#             # Highlight parity bits if old_blocks is not provided
#             block_index = i % len(encoded_blocks[0])
#             if block_index in parity_positions:
#                 code += f"{BLUE}{new_code[i]}{RESET}"
#             else:
#                 code += new_code[i]
#     print(code)

def print_blocks(
    encoded_blocks: list[list[int]],
    old_blocks: list[list[int]] = None,
):
    RESET = "\033[0m"
    BLUE = "\033[94m"
    GREEN = "\033[32m"
    RED = "\033[91m"

    r = int(math.log2(len(encoded_blocks[0]) + 1))
    parity_positions = range(len(encoded_blocks[0]) - r, len(encoded_blocks[0]) + 1)
    old_code = (
        "".join("".join(map(str, block)) for block in old_blocks)
        if old_blocks
        else None
    )
    new_code = "".join("".join(map(str, block)) for block in encoded_blocks)

    code = ""
    for i in range(len(new_code)):
        if i % len(encoded_blocks[0]) == 0 and i != 0:
            code += " "
        if old_blocks:
            # Highlight differences if old_blocks is provided
            if old_code[i] == new_code[i]:
                code += f"{GREEN}{new_code[i]}{RESET}"
            else:
                code += f"{RED}{new_code[i]}{RESET}"
        else:
            # Highlight parity bits if old_blocks is not provided
            block_index = i % len(encoded_blocks[0])
            if block_index in parity_positions:
                code += f"{BLUE}{new_code[i]}{RESET}"
            else:
                code += new_code[i]
    print(code)


def print_data_with_padding(
    data: list[int], padding_bits: int, data_bits_per_block: int
):
    """Print data with padding bits highlighted in yellow."""
    YELLOW = "\033[93m"
    RESET = "\033[0m"

    data_str = ""
    padding_start = len(data) - padding_bits

    for i, bit in enumerate(data):
        # Add space between blocks
        if i % data_bits_per_block == 0 and i != 0:
            data_str += " "

        # Color padding bits yellow
        if i >= padding_start:
            data_str += f"{YELLOW}{bit}{RESET}"
        else:
            data_str += str(bit)

    print(data_str)
