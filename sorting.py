#!/bin/python

import json
import os
import re
import subprocess
import sys


class Sorting:
    def __init__(self):
        self.formats = {}
        self.settings = {}
        self.import_formats()

    def process(self, args):
        while True:
            match args[0:2]:
                case [("-h" | "--help")]:
                    print(
                        "Usage: sorting.py [-a category:format] [-d format] [-i path] [--edit-sorting-folder path] [--dump-config] [--dump-config-file path] [--add-origin-folder path] [--remove-origin-folder path] [[-n] | [format] | None]"
                    )
                    break
                case ["-a", arg]:
                    self.__add_new_format(*arg.split(":"))
                    self.save_settings()
                case ["-r", arg]:
                    ...
                case ["-d", arg]:
                    self.__delete_format(arg)
                    self.save_settings()
                case ["-i", arg]:
                    self.__import_settings(arg)
                case ["--edit-sorting-folder", arg]:
                    self.__edit_sorting_folder(arg)
                    quit()
                case ["--add-origin-folder", arg]:
                    self.__add_origin_folder(arg)
                    quit()
                case ["--remove-origin-folder", arg]:
                    self.__remove_origin_folder(arg)
                    quit()
                case ["--dump-config"]:
                    print(self.__dump_config())
                    quit()
                case ["--dump-config-file", arg]:
                    self.__dump_config_file(arg)
                    quit()
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
                    quit()
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
                break
        else:
            print("Unknown format")

    def __import_settings(self, file_from):
        try:
            with open(file_from) as f:
                data = json.load(f)
                self.formats = data["formats"]
                self.settings = data["settings"]
                self.save_settings()
        except FileNotFoundError:
            self.formats = {}
            self.settings = {}

    def __edit_sorting_folder(self, folder_path):
        self.settings["main_folder"] = (folder_path + "/").replace("//", "/")
        self.save_settings()

    def __dump_config(self):
        return {"settings": self.settings, "formats": self.formats}

    def __dump_config_file(self, file_path):
        with open(file_path, "w") as f:
            json.dump(self.__dump_config(), f, indent=4)

    def __add_origin_folder(self, folder_path):
        new_folder = (folder_path + "/").replace("//", "/")
        if new_folder not in self.settings["source_folder"]:
            self.settings["source_folder"] += f"^{new_folder}"
        self.save_settings()

    def __remove_origin_folder(self, folder_path):
        self.settings["source_folder"] = self.settings["source_folder"].replace(
            f"^{(folder_path + '/').replace('//', '').replace('~', os.path.expanduser('~'))}/",
            "",
        )
        self.save_settings()

    def sorting(self, thisformat=None):
        if thisformat == None:
            thisformat = r".*"
        for category, formats in self.formats.items():
            subprocess.run(
                ["mkdir", "-p", f"{self.settings['main_folder']}/{category}"]
            )
            catFiles = []
            for format in formats:
                if re.match(thisformat, format):
                    for dir in self.settings["source_folder"].split("^"):
                        files = subprocess.run(
                            ["fd", "--max-depth", "1", rf"\.{format}", dir],
                            stdout=subprocess.PIPE,
                        )
                        files_output = list(
                            map(
                                lambda x: (x, x.replace(dir, "")),
                                files.stdout.decode().splitlines(),
                            )
                        )
                        for file, relative_path in files_output:
                            subprocess.run(
                                [
                                    "mv",
                                    "-v",
                                    file,
                                    f"{self.settings['main_folder']}{category}/"
                                    + relative_path,
                                ]
                            )
                    quit()
        print("Unknown argument")
        quit()

    def get_formats_path(self):
        return os.path.join(os.path.expanduser("~/.config/sorting"), "formats.json")

    def import_formats(self):
        file_path = self.get_formats_path()
        if not os.path.exists(file_path):
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "w") as file:
                json.dump({}, file)
        with open(file_path) as file:
            data = json.load(file)
        self.settings = data["settings"]
        if not self.settings["source_folder"]:
            self.settings["source_folder"] = "~/"
        self.settings["main_folder"] = self.settings["main_folder"].replace(
            "~", os.path.expanduser("~")
        )
        self.settings["source_folder"] = self.settings["source_folder"].replace(
            "~", os.path.expanduser("~")
        )
        self.formats = data["formats"]

    def save_settings(self):
        data = {"settings": self.settings, "formats": self.formats}

        file_path = self.get_formats_path()
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)


if __name__ == "__main__":
    Sorting().process(sys.argv[1:])
