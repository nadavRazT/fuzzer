import random
import sys
from jpg_decoder.Decoder import Decoder
import numpy as np
import json

FLIP_RATIO = 0.3

IFD = ["IFD0", "subIFD", "IFD1"]

IFD_IND = 0
OFFSET_IND = 1
DN_IND = 2
ENTRY_IND = 3
CHANGE = 1
KEEP = 0
ADDRESS_SIZE = 4
DN_SIZE = 2
VEC_ENTRY_SIZE = 6
TAG_IND = 0
FORMAT_IND = 1
NUM_IND = 2
VAL_IND = 3
CHANGE_DAT_IND = 4
ADDRESS = "address"

FLIPS = 4

MAGIC_VALS = [
    [0xFF],
    [0x7F],
    [0x00],
    [0xFF, 0xFF],  # 0xFFFF
    [0x00, 0x00],  # 0x0000
    [0xFF, 0xFF, 0xFF, 0xFF],  # 0xFFFFFFFF
    [0x00, 0x00, 0x00, 0x00],  # 0x80000000
    [0x00, 0x00, 0x00, 0x80],  # 0x80000000
    [0x00, 0x00, 0x00, 0x40],  # 0x40000000
    [0xFF, 0xFF, 0xFF, 0x7F],  # 0x7FFFFFFF
    [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0x7F]
]


class Mutator:

    def __init__(self, config):
        self.config = config
        image_name = config["source"]
        self.o_image_name = image_name
        self.o_image_file = open(image_name, "rb")
        self.o_data = self.o_image_file.readlines()
        jpgDecoder = Decoder(image_name)
        self.o_json = jpgDecoder.decode()
        self.mutated_json = {}

    ### ---------- CREATE VECTORS -------- ###

    def mutate_change_vector_for_ifd(self, vec):
        flip_indexes = random.choices(range(len(vec)), k=FLIPS)
        for ind in flip_indexes:
            vec[ind] = CHANGE
        vec[0] = random.choice([KEEP, CHANGE])
        return vec

    def randomize_change_vector(self):
        ifd0_vec_len = (3 + 6 * self.o_json["APP1"]["IFD0"]["Directory"]["Directory number"]["data"])
        subifd_vec_len = (3 + 6 * self.o_json["APP1"]["subIFD"]["Directory"]["Directory number"]["data"])
        ifd1_vec_len = (3 + 6 * self.o_json["APP1"]["IFD1"]["Directory"]["Directory number"]["data"])
        ifd0_vec = self.mutate_change_vector_for_ifd(np.zeros(ifd0_vec_len))
        subifd_vec = self.mutate_change_vector_for_ifd(np.zeros(subifd_vec_len))
        ifd1_vec = self.mutate_change_vector_for_ifd(np.zeros(ifd1_vec_len))

        cv = {"IFD0": ifd0_vec, "subIFD": subifd_vec,
              "IFD1": ifd1_vec}
        return cv

    ### ---------- MUTATE BY VECTORS -------- ###
    def mutate_offset(self, ifd_offset):
        ifd_offset["data"] = self.get_magic(ADDRESS_SIZE)
        return ifd_offset

    def mutate_dn(self, dn):
        dn["data"] = self.get_magic(DN_SIZE)
        return dn

    def mutate_entries(self, entries_list, vec):
        mutated_entries = []
        for i in range(len(entries_list)):
            entry_vec = vec[ENTRY_IND + i * VEC_ENTRY_SIZE: ENTRY_IND + (i + 1) * VEC_ENTRY_SIZE]
            if (entry_vec[0]) == KEEP:
                continue
            mutated_entries += [self.mutate_entry(entries_list[i], entry_vec)]
        return mutated_entries

    def mutate_entry(self, entry_json, entry_vec):
        entry_json["data addressed"] = {"address": "", "data": ""}
        if entry_vec[TAG_IND] == CHANGE:
            entry_json["Tag number"]["data"] = self.get_magic(2)
        num_componnents = entry_json["component num"]["data"]
        format = entry_json["data format"]["data"]
        size = entry_json["data format"]["enterp"]["size"]
        if entry_vec[FORMAT_IND] == CHANGE:
            entry_json["data format"]["data"] = np.random.randint(8)  # todo check maybe random between 1 -8

        if entry_vec[NUM_IND] == CHANGE:
            entry_json["component num"]["data"] = self.get_magic(4)

        if entry_vec[CHANGE_DAT_IND] == CHANGE and entry_json["data type"] == ADDRESS:
            entry_json["data addressed"]["address"] = int(entry_json["data value"]["data"], 16)
            entry_json["data addressed"]["data"] = b''.join([self.get_magic(size) for i in range(num_componnents)])

        if entry_vec[VAL_IND] == CHANGE:
            entry_json["data value"]["data"] = self.get_magic(4)
        return entry_json

    def mutate_ifd_by_vector(self, vec, ifd_json):
        mutated_ifd = {"IFD offset": {}, "Directory": {"Directory number": {}, "Entries": []}}
        if vec[OFFSET_IND] == CHANGE:
            mutated_ifd["IFD offset"] = self.mutate_offset(ifd_json["IFD offset"])
        if vec[DN_IND] == CHANGE:
            mutated_ifd["Directory"]["Directory number"] = self.mutate_offset(ifd_json["Directory"]["Directory number"])
        mutated_entries = self.mutate_entries(ifd_json["Directory"]["Entries"], vec)
        mutated_ifd["Directory"]["Entries"] = mutated_entries
        return mutated_ifd

    def mutate_app1(self, change_vec):
        # use change vector
        for ifd in IFD:
            if change_vec[ifd][IFD_IND] == KEEP:
                self.mutated_json[ifd] = {}
                continue
            ifd_json = self.o_json["APP1"][ifd]
            self.mutated_json[ifd] = self.mutate_ifd_by_vector(change_vec[ifd], ifd_json)
        return

    def mutate_sos(self):
        self.mutated_json["SOS"] = 0  # todo change header

    ### ------------------------------------- ###

    def mutate_jpg(self):
        self.change_vector = self.randomize_change_vector()
        self.mutate_app1(self.change_vector)
        print(self.mutated_json)
        return

    def mutate_directory(self, directory):
        return directory

    def bit_flip(self, byte):
        if not byte:
            return
        r = random.choice([1, 2, 4, 8, 16, 32, 64, 128])
        return self.b_i_xor(byte, r)

    def b_i_xor(self, b1, i1):
        b1 = b1[:len(str(i1))]
        int_key = int.from_bytes(b1, sys.byteorder)
        int_enc = i1 ^ int_key
        return int_enc.to_bytes(len(str(i1)), sys.byteorder)

    def magic(self, data, idx):
        picked_magic = random.choice(MAGIC_VALS)
        offset = 0
        for m in picked_magic:
            data[idx + offset] = m.to_bytes(2, 'big')
            offset += 1
        return data

    def get_magic(self, n_bytes):
        m = []
        while len(m) != n_bytes:
            m = random.choice(MAGIC_VALS)
        a = bytes()
        for b in m:
            a += b.to_bytes(1, "big")
        # a = int.from_bytes(a, "big")
        return a

    def mutate(self):
        self.mutate_jpg()
        config = self.config
        data = self.o_data
        flips = int((len(data) - 4) * FLIP_RATIO)
        flip_indexes = random.choices(range(2, (len(data) - 6)), k=flips)
        methods = [0, 1]
        for idx in flip_indexes:
            c = random.choice(methods)
            if c == 0:
                data[idx] = self.bit_flip(data[idx])
            elif c == 1:
                data = self.magic(data, idx)

        with open(config["file"], "wb") as f:
            f.writelines(data)
        return data


if __name__ == '__main__':
    config = {
        "file": "data/mutated.jpg",
        "source": "data/test.jpg",
        "target": ""
    }
    mutator = Mutator(config)
    mutator.mutate_jpg()
