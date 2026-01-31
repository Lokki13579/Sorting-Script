#!/bin/python

import json
import re
import subprocess
import sys


class Sorting:
    def __init__(self):
        self.formats = {}
        self.import_formats()

    def process(self, args):
        while True:
            match args[0:2]:
                case [("-h" | "--help")]:
                    print(
                        "Usage: sorting.py [-a category:format] [-d format] [[-n] | [format] | None]"
                    )
                case ["-a", arg]:
                    new_category, new_format = arg.split(":")
                    if new_category not in self.formats:
                        self.formats[new_category] = []
                    if new_format not in self.formats[new_category]:
                        self.formats[new_category].append(new_format)
                    self.save_formats()
                case ["-d", arg]:
                    for key, vals in self.formats.items():
                        if arg in vals:
                            vals.remove(arg)
                            self.save_formats()
                            print("removed", arg)
                            break
                    else:
                        print("Unknown format")
                case ["-n"]:
                    break
                case [format]:
                    self.sorting(format)
                    break
                case []:
                    self.sorting()
                    break
                case _:
                    print("Unknown argument")
                    break
            args = args[2:]

    def sorting(self, thisformat=None):
        if thisformat == None:
            thisformat = r".*"
        print("sorting")
        for category, formats in self.formats.items():
            subprocess.run(["mkdir", "-p", f"/home/artem/files/{category}"])
            for format in formats:
                if re.match(thisformat, format):
                    subprocess.run(
                        [
                            "fd",
                            "--max-depth",
                            "1",
                            rf"\.{format}",
                            "/home/artem/",
                            "-x",
                            "mv",
                            "-v",
                            "{}",
                            f"/home/artem/files/{category}/" + "{/}",
                        ],
                        stdout=subprocess.PIPE,
                    )

    def import_formats(self):
        with open("formats.json") as file:
            self.formats = json.load(file)
        print("imported", self.formats)

    def save_formats(self):
        print(self.formats, "- saving")
        with open("formats.json", "w", encoding="utf-8") as f:
            json.dump(self.formats, f, indent=4)


print(sys.argv[1:])
if __name__ == "__main__":
    Sorting().process(sys.argv[1:])
