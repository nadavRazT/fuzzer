import numpy as np
import random

FLIP_RATIO = 0.01


def mutate(data):
    flips = int((len(data) - 4) * FLIP_RATIO)
    flip_indexes = random.choices(range(2, (len(data) - 6)), k=flips)
    for idx in flip_indexes:
        data[idx] = bit_flip(data[idx])
    return data


def bit_flip(byte):
    if not byte:
        return
    return bxor(bytes(random.choice([1,2,4,8,16,32,64,128])), byte)


def bxor(b1, b2):
    return bytes([_a ^ _b for _a, _b in zip(b1, b2)])

if __name__ == "__main__":
    file = open("data/test.jpg", "rb")
    data = file.readlines()
    file.close()

    data = mutate(data)
    file = open("data/mutated.jpg", "wb")
    file.writelines(data)
