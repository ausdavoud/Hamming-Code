import math
import random
from copy import deepcopy
from itertools import batched

import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import root_scalar

from tools import print_blocks, print_data_with_padding


# def generate_H_transpose(r: int) -> list[list[int]]:
#     return [[int(bit) for bit in f"{i:0{r}b}"] for i in range(1, 2**r)]
def generate_H_transpose(r: int, move_I: bool = False) -> list[list[int]]:
    if not move_I:
        return [[int(bit) for bit in f"{i:0{r}b}"] for i in range(1, 2**r)]
    parity_positions = [2**i for i in range(r)]
    H = [
        [int(bit) for bit in f"{i:0{r}b}"]
        for i in range(1, 2**r)
        if i not in parity_positions
    ]
    H += [
        [int(bit) for bit in f"{i:0{r}b}"]
        for i in range(2**r, 0, -1)
        if i in parity_positions
    ]
    return H


def transpose(H: list[list[int]]):
    return [[H[j][i] for j in range(len(H))] for i in range(len(H[0]))]


def generate_H(r: int, move_I: bool) -> list[list[int]]:
    H_transpose = generate_H_transpose(r, move_I=move_I)
    return transpose(H_transpose)


def generate_G(H: list[list[int]]) -> list[list[int]]:
    # Extract the first r*r sub-matrix in H
    r = len(H)
    row_width = len(H[0])
    data_bits = row_width - r  # Number of data bits
    P_transpose = [row[:data_bits] for row in H]  # Extract the parity part
    # Transpose it
    P = transpose(P_transpose)

    # Identity matrix of size data_bits x data_bits
    I = [[1 if i == j else 0 for j in range(data_bits)] for i in range(data_bits)]
    # Generate G matrix
    G = []
    for i in range(data_bits):
        G.append(I[i] + P[i])
    return G


def multiply_matrices(A: list[list[int]], B: list[list[int]]) -> list[list[int]]:
    """Multiplies two matrices A and B."""
    result = [[0 for _ in range(len(B[0]))] for _ in range(len(A))]
    for i in range(len(A)):
        for j in range(len(B[0])):
            for k in range(len(B)):
                result[i][j] ^= A[i][k] & B[k][j]
    return result


def generate_block(r: int):
    return [0] * (2**r - 1)


# def encode_data_blocks2(data: list[int], r: int, H: list[list[int]]) -> list[list[int]]:
#     data_bits_per_block = 2**r - 1 - r
#     encoded_blocks = list()
#     for i in range(0, len(data), data_bits_per_block):
#         data_chunk = data[i : i + data_bits_per_block]

#         block = generate_block(r=r)
#         fill_parity_bits_with_None(block)
#         put_data_on_block(block, data_chunk)

#         parity_bits = calculate_parity_bits(block, H)
#         parity_bits.reverse()
#         fill_parity_bits_with_xor(block, parity_bits)

#         encoded_blocks.append(block)
#     return encoded_blocks


def encode_data_blocks(data: list[int], G: list[list[int]]) -> list[list[int]]:
    data_bits_per_block = len(G)
    encoded_blocks = []
    for i in range(0, len(data), data_bits_per_block):
        data_chunk = data[i : i + data_bits_per_block]
        block = multiply_matrices([data_chunk], G)[0]  # Multiply data chunk by G
        encoded_blocks.append(block)
    return encoded_blocks


def fill_parity_bits_with_None(block: list[int]):
    r = int(math.log2(len(block) + 1))
    parity_positions = [2**i - 1 for i in range(r)]
    for pos in parity_positions:
        block[pos] = None


def put_data_on_block(block: list[int], data: list[int]):
    data_iter = iter(data)
    for i in range(len(block)):
        if block[i] is None:  # Parity bit is initially `None`
            continue
        block[i] = next(data_iter, 0)


def calculate_parity_bits(block: list[int], H: list[list[int]]):
    parity_bits = []
    for i in range(len(H)):
        local_sum = 0
        for j in range(len(H[0])):
            if H[i][j] == 0 or block[j] is None:
                continue
            local_sum ^= block[j]
        parity_bits.append(local_sum)
    return parity_bits


def fill_parity_bits_with_xor(block: list[int], parity_bits: list[int]):
    r = int(math.log2(len(block) + 1))
    for i in range(r):
        block[2**i - 1] = parity_bits[i]


def generate_error(all_blocks: list[list[int]], p: float):
    channel_error = random.choices(
        [1, 0], [p, 1 - p], k=len(all_blocks) * len(all_blocks[0])
    )
    channel_error = iter(channel_error)
    for i in range(len(all_blocks)):
        for j in range(len(all_blocks[i])):
            all_blocks[i][j] = all_blocks[i][j] ^ next(channel_error)


def find_error_index(H_transpose: list[list[int]], parity_bits: list[int]):
    for i in range(len(H_transpose)):
        if H_transpose[i] == parity_bits:
            return i
    return -1


def fix_error_at_index(block: list[int], index: int):
    block[index] = 1 - block[index]


def pad_data(data: list[int], block_size: int) -> tuple[list[int], int]:
    """Pad the data to fit into blocks of size `block_size`."""
    padding_needed = math.ceil(len(data) / block_size)
    padding_needed = (padding_needed * block_size) - len(data)
    data.extend([0] * padding_needed)
    return data, padding_needed


# def correct_errors(blocks: list[list[int]], H: list[list[int]]):
#     errors_corrected = 0

#     for block in blocks:
#         new_parity_bits = calculate_parity_bits(block, H)
#         error_index = find_error_index(new_parity_bits)

#         if error_index != 0:
#             fix_error_at_index(block, error_index)
#             errors_corrected += 1
#     return errors_corrected


def correct_errors(blocks: list[list[int]], H_transpose: list[list[int]]):
    errors_corrected = 0

    for block in blocks:
        new_parity_bits = multiply_matrices([block], H_transpose)[0]
        error_index = find_error_index(H_transpose, new_parity_bits)

        if error_index != -1:
            fix_error_at_index(block, error_index)
            errors_corrected += 1
    return errors_corrected


def decode_blocks(blocks: list[list[int]]) -> list[list[int]]:
    r = int(math.log2(len(blocks[0]) + 1))
    decoded_data = []

    for block in blocks:
        data_bits = block[:-r]
        decoded_data.append(data_bits)
    return decoded_data


def get_error_count(decoded_data: list[int], original_data: list[int]) -> int:
    error_count = 0
    for i in range(len(decoded_data)):
        if decoded_data[i] != original_data[i]:
            error_count += 1
    return error_count


def main(r, error_probability, data_length):
    # r = int(input("Enter the number of parity bits (r): "))
    # r = 3
    # error_probability = 0.1
    data_bits_per_block = 2**r - 1 - r

    # print(f"Hamming({data_bits_per_block + r}, {data_bits_per_block}) Code")
    # print(
    #     f"Block size: {data_bits_per_block + r} bits, Data bits: {data_bits_per_block} bits, Parity bits: {r} bits"
    # )
    # print("-" * 50)

    # Generate test data
    data = [random.randint(0, 1) for _ in range(data_length)]  # Random data for testing
    # data = "01011100101"
    data = [int(bit) for bit in data]

    printable = data_length < 100
    if printable:
        print("Data before padding:")
        print_data_with_padding(data, 0, data_bits_per_block)
    data, padding_bits_num = pad_data(data, data_bits_per_block)

    if printable:
        print(f"Original data: {len(data)} bits, Padding added: {padding_bits_num} bits")
        print("Data after padding:")
        print_data_with_padding(data, padding_bits_num, data_bits_per_block)

    # num_blocks = len(data) // (data_bits_per_block)

    # Create H matrix
    H = generate_H(r, move_I=True)

    
    G = generate_G(H)

    encoded_blocks = encode_data_blocks(data, G)
    if printable:
        print("Encoded blocks:")
        print_blocks(encoded_blocks)

    if printable:
        print(f"Introducing errors: (p={error_probability})...")
    old_blocks = deepcopy(encoded_blocks)
    generate_error(encoded_blocks, p=error_probability)
    if printable:
        print_blocks(encoded_blocks=encoded_blocks, old_blocks=old_blocks)

    if printable:
        print("Correcting errors...")
    H_transpose = transpose(H)
    errors_corrected = correct_errors(encoded_blocks, H_transpose)

    if printable:
        print_blocks(encoded_blocks=encoded_blocks, old_blocks=old_blocks)
        print(f"Errors corrected: {errors_corrected}")

    decoded_data = decode_blocks(encoded_blocks)
    if printable:
        print("Real data after padding:")
        print_data_with_padding(data, padding_bits_num, data_bits_per_block)
        print("Data after decoding:")
        print_blocks(
            encoded_blocks=decoded_data, old_blocks=list(batched(data, data_bits_per_block))
        )

    if printable:
        print("Data after removing padding:")
    for i in range(padding_bits_num):
        decoded_data[-1].pop()

    if printable:
        print_blocks(decoded_data, old_blocks=list(batched(data, data_bits_per_block)))

    flatten_decoded_data = [j for i in decoded_data for j in i]
    error_count = get_error_count(flatten_decoded_data, data)
    error_rate = error_count / len(flatten_decoded_data)
    return error_rate


def solve_for_p(r):
    def H(p):
        if p <= 0 or p >= 1:
            return 0.0
        return p * np.log2(p) + (1 - p) * np.log2(1 - p)

    C = (2**r - 1 - r) / (2**r - 1)

    return root_scalar(lambda p: 1 + H(p) - C, bracket=[1e-10, 0.5 - 1e-10]).root


if __name__ == "__main__":
    rates = []
    r = int(input("Enter the number of parity bits (r): "))
    data_length = int(input("Enter the data length: "))
    # r = 7
    # data_length = 10000
    shannon_p = solve_for_p(r=r)
    print("shannon p is: ", shannon_p)
    plt.axvline(
        x=(1 - shannon_p) / shannon_p, color="r", linestyle="--", label="x = 3/4"
    )
    print(f"Shannon's limit for r={r}: p = {shannon_p}")
    print(f"Shannon's limit for r={r}: (1-p)/p = {(1 - shannon_p) / shannon_p}")
    print("-" * 50)
    for p in range(1, 49):
        # for p in [0.49, 0.3, 0.1, 0.01, 0.001]:
        p /= 100
        error_rate = main(r=r, error_probability=p, data_length=data_length)
        rates.append(((1 - p) / p, error_rate))
        print(f"Error probability: {p}")
        print(f"Error rate: {error_rate}")
        print("-" * 50)

    # Unzip the list of tuples into two lists: x and y
    x, y = zip(*rates)

    # Create the plot
    plt.plot(x, y, marker="o")  # You can use other markers/lines if preferred

    # Label the axes
    plt.xlabel(r"(1-p)/p")
    plt.ylabel(r"P_error")
    plt.title("Plot of (x, y) tuples")

    plt.yscale("log")  # Set x-axis to logarithmic scale
    plt.yticks([10**i for i in range(-1, -4, -1)])
    # Show the plot
    plt.show()
