import json

EXIF_TAGS_FILENAME = "jpg_decoder/exifData.json"

class Decoder:
    def __init__(self, filename):
        # self.file = open("none.txt", "rb+")# file
        with open(EXIF_TAGS_FILENAME) as f:
            self.exif_tags = json.load(f)["ExifTags"]

        with open(EXIF_TAGS_FILENAME) as f:
            self.data_format = json.load(f)["DataFormat"]
        with open(filename, "rb+") as f:
            self.file_data = f.read()

        self.pointer = 0
        self.header_offset = 0
        self.json = {}

    def decode(self):
        sos = self.read(2).hex()
        self.json["SOS"] = str(sos)
        self.json["APP1"] = self.app1_decoder()
        with open("json_file.json", "w") as f:
            json.dump(self.json, f)
        return self.json

    def app1_decoder(self):
        app1 = {}
        app1["APP1 Marker"] = str(self.read(2).hex())
        app1["APP1 Size"] = str(self.read(2).hex())
        app1["Exif Header"] = str(self.read(6).hex())
        app1["TIFF Header"] = self.TIFF_decoder()

        app1["IFD0"] = self.IFD_decoder()

        subIFD_link = self.get_subIFD_link(app1["IFD0"])
        self.pointer = subIFD_link + self.header_offset
        app1["subIFD"] = self.IFD_decoder()

        IFD1_link = self.get_IFD1_link(app1["IFD0"])
        self.pointer = IFD1_link + self.header_offset
        app1["IFD1"] = self.IFD_decoder()
        return app1

    def TIFF_decoder(self):
        tiff = {}
        self.header_offset = self.pointer
        tiff["Byte align"] = str(self.read(2).hex())
        tiff["Tag mark"] = str(self.read(2).hex())
        tiff["Link"] = str(self.read(4).hex())
        return tiff

    def IFD_decoder(self):
        ifd = {}
        ifd["Directory"] = self.directory_decoder()
        ifd["IFD offset"] = {"address" : self.pointer, "data": str(self.read(4).hex())}
        return ifd

    def directory_decoder(self):
        directory = {}
        entry_num = int.from_bytes(self.read(2), "big")
        directory["Directory number"] = {"address": self.pointer - 2, "data" :entry_num}
        directory["Entries"] = [self.entry_decoder(self.read(12)) for i in range(entry_num)]
        return directory

    def entry_decoder(self, to_dec):
        entry = {}
        pointer = self.pointer
        entry["Tag number"] = {"address": pointer - 12, "data": str(to_dec[0:2].hex())}
        entry["data format"] = {"address": pointer - 10,
                                "enterp": self.data_format[str(int(str(to_dec[2:4].hex()), 16))],
                                "data":int(str(to_dec[2:4].hex()), 16) }
        entry["component num"] = {"address": pointer - 8,"data": int(str(to_dec[4:8].hex()), 16)}
        entry["data value"] = {"address" : pointer -4, "data" : str(to_dec[8:12].hex())}

        if entry["data format"]["enterp"]["size"] * entry["component num"]["data"] > 8:
            entry["data type"] = "address"
        else:
            entry["data type"] = "data"

        return entry

    def get_subIFD_link(self, IFD0):
        directory = IFD0["Directory"]
        entries = directory["Entries"]
        for entry in entries:
            if entry["Tag number"]["data"] == self.exif_tags["ExifOffset"]:
                return int(entry["data value"]["data"], 16)

    def get_IFD1_link(self, IFD0):
        return int(IFD0["IFD offset"]["data"], 16)

    def read(self, i):
        self.pointer += i
        return self.file_data[self.pointer - i:self.pointer]
