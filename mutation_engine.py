import numpy as np
import random
import sys
import time

FLIP_RATIO = 0.3


def mutate(data):
    flips = int((len(data) - 4) * FLIP_RATIO)
    flip_indexes = random.choices(range(2, (len(data) - 6)), k=flips)
    for idx in flip_indexes:
        data[idx] = bit_flip(data[idx])
    return data


def bit_flip(byte):
    if not byte:
        return
    r = random.choice([1,2,4,8,16,32,64,128])
    return b_i_xor(byte, r)



def b_i_xor(b1, i1):
    b1 = b1[:len(str(i1))]
    int_key = int.from_bytes(b1, sys.byteorder)
    int_enc = i1 ^ int_key
    return int_enc.to_bytes(len(str(i1)), sys.byteorder)

if __name__ == "__main__":
    file = open("data/test.jpg", "rb")
    data = file.readlines()
    file.close()

    data = mutate(data)
    file = open("data/mutated.jpg", "wb")
    file.writelines(data)
