import numpy as np
import random
import sys
import time

FLIP_RATIO = 0.3

MAGIC_VALS = [
  [0xFF],
  [0x7F],
  [0x00],
  [0xFF, 0xFF], # 0xFFFF
  [0x00, 0x00], # 0x0000
  [0xFF, 0xFF, 0xFF, 0xFF], # 0xFFFFFFFF
  [0x00, 0x00, 0x00, 0x00], # 0x80000000
  [0x00, 0x00, 0x00, 0x80], # 0x80000000
  [0x00, 0x00, 0x00, 0x40], # 0x40000000
  [0xFF, 0xFF, 0xFF, 0x7F], # 0x7FFFFFFF
]


def create_mutation(config):
    with open(config["source"], "rb") as f:
        data = f.readlines()

    data = mutate(data)
    with open(config["file"], "wb") as f:
        f.writelines(data)
    return data


def magic(data, idx):
    picked_magic = random.choice(MAGIC_VALS)
    offset = 0
    for m in picked_magic:
        data[idx + offset] = m.to_bytes(2, 'big')
        offset += 1
    return data

def mutate(data):
    flips = int((len(data) - 4) * FLIP_RATIO)
    flip_indexes = random.choices(range(2, (len(data) - 6)), k=flips)
    methods = [0, 1]
    for idx in flip_indexes:
        c = random.choice(methods)
        if c == 0:
            data[idx] = bit_flip(data[idx])
        elif c == 1:
            data = magic(data, idx)
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
