class Decoder:
    def __init__(self):
        # self.file = open("none.txt", "rb+")# file
        
        self.json = {}


    def decode(self, file):
        self.file = file
        sos = self.file.read(2)
        self.json["SOS"] = sos
        self.json["APP1"] = self.app1_decoder()
        return self.json


    def app1_decoder(self):
        app1 = {}
        app1["APP1 Marker"] = self.file.read(2)
        app1["APP1 Size"] = self.file.read(2)
        app1["Exif Header"] = self.file.read(6)
        app1["TIFF Header"] = self.TIFF_decoder()
        app1["IFD"] = self.IFD_decoder()
        return app1

    def TIFF_decoder(self):
        tiff = {}
        tiff["Byte align"] = self.file.read(2)
        tiff["Tag mark"] = self.file.read(2)
        tiff["Link"] = self.file.read(4)
        return tiff

    def IFD_decoder(self):
        return

    def directory_decoder(self):
        return

    def entry_decoder(self):
        return