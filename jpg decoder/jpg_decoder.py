import numpy as np
import exifread
import Decoder


def jpg_decoder(filename):
    decoder = Decoder.Decoder()
    with open(filename, "rb+") as f:
        print(decoder.decode(f))


if __name__ == '__main__':
    jpg_decoder("data/test.jpg")
