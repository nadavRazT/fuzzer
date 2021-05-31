import numpy as np
import exifread
import Decoder
import json
import hexson


def jpg_decoder(filename):
    decoder = Decoder.Decoder(filename)
    with open(filename, "rb+") as f:
        jsn = decoder.decode()
    # parse_jpg(filename)
    with open("json_file.json", "w") as f:
        json.dump(jsn, f, indent=4)


def parse_jpg(filename):
    with open(filename,"rb+") as f:
        _ = f.read()
        print("length of file -> ", len(_))
    with open(filename, "rb+") as f:
        byte = f.read(1)
        i = 0
        while byte:
            n = 100
            if i < 220 and i > 205:
                print(i," " ,hex(i), " ", hex(byte[0]), " ", byte,"->", int(byte[0]))
            byte = f.read(1)
            i += 1


if __name__ == '__main__':
    jpg_decoder("data/test.jpg")
