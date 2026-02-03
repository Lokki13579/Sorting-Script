#!/bin/python

import json
import os
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
                    break
                case ["-a", arg]:
                    self.__add_new_format(*arg.split(":"))
                    self.save_formats()
                case ["-r", arg]:
                    old_category, new_category = arg.split(":")
                    if old_category not in self.formats:
                        self.formats[old_category] = []
                    if new_category not in self.formats:
                        self.formats[new_category] = []
                    for cat, formats in self.formats.items():
                        if old_category in formats:
                            formats.remove(old_category)
                            self.formats[new_category].append(old_category)
                            self.save_formats()
                            print("moved", old_category, "to", new_category)
                            break
                    else:
                        print("Unknown category")
                case ["-d", arg]:
                    self.__delete_format(arg)
                    self.save_formats()
                case ["-i", arg]:
                    self.__import_settings(arg)
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

    def __add_new_format(self, category, format):
        if category not in self.formats:
            self.formats[category] = []
        self.__delete_format(format)
        self.formats[category].append(format)

    def __delete_format(self, format):
        for key, vals in self.formats.items():
            if format in vals:
                vals.remove(format)
                print("removed", format)
                break
        else:
            print("Unknown format")

    def __import_settings(self, file_from):
        try:
            with open(file_from) as f:
                self.formats = json.load(f)
                self.save_formats()
        except FileNotFoundError:
            self.formats = {}

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

    def get_formats_path(self):
        return os.path.join(os.path.expanduser("~/.config/sorting"), "formats.json")

    def import_formats(self):
        file_path = self.get_formats_path()
        if not os.path.exists(file_path):
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "w") as file:
                json.dump({}, file)
        with open(file_path) as file:
            self.formats = json.load(file)
        print("imported", self.formats)

    def save_formats(self):
        print(self.formats, "- saving")
        file_path = self.get_formats_path()
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(self.formats, f, indent=4)


if __name__ == "__main__":
    Sorting().process(sys.argv[1:])
