"""Parses Megapede data."""
import logging
import struct
import os
from collections import namedtuple

import yapsy
from jinja2 import Environment, FileSystemLoader

import utilities
from errors import UnsupportedSoftwareException
from utilities import File, FileReader


env = Environment(loader=FileSystemLoader('./formats'))

class Megapede(yapsy.IPlugin.IPlugin):
    """Parses Megapede data."""

    key = "cheesy_megapede_a"
    title = "Megapede"
    developer = "Cheesy Software"
    description = "Megapede (Cheesy Software) v1.3c"

    identifying_files = [
        File("MEGAPEDE.EXE", 89844,  "60de7f0f904c0edd86c6ac4069e109f6"),
        File("MEGACORE.EXE", 126448, "fce9aa8e9937211874efdbe8d88260be"),
    ]
    scorefile = "MEGAPEDE.SCO"

    score_reader = FileReader([
        ("name", "10s"),
        ("padding", "x"), # Unknown meaning. Issue #1.
        ("score", "I"),
        ("level", "B"),
        ])

    @staticmethod
    def export(path, format="html"):
        """Exports everything this class supports."""
        if not Megapede.verify(path):
            raise UnsupportedSoftwareException
        global env
        if format == "html":
            template = env.get_template('Megapede.html')
        text = template.render({
            "key" : Megapede.key,
            "title" : Megapede.title,
            "developer" : Megapede.developer,
            "description" : Megapede.description,
            "high_score_table" : Megapede.read_scores(path),
            "resources" : Megapede.extract_rd(path),
            })
        return text

    @staticmethod
    def verify(path):
        """Verifies that the provided path is the supported game."""
        return utilities.verify(Megapede.identifying_files, path)

    @staticmethod
    def read_scores(path):
        """Reads score file foound in path."""
        scores = []
        with open(os.path.join(path, Megapede.scorefile), "rb") as scorefile:
            for data in iter(lambda: scorefile.read(Megapede.score_reader.struct.size), b""):
                scores.append(Megapede.score_reader.unpack(data))
        return scores

    @staticmethod
    def extract_resources(path):
        """Extract resources from MEGAPEDE.RES."""
        resources = Megapede.extract_rd(path)
        with open(path + "MEGAPEDE.RES", "rb") as infile:
            for res in resources:
                infile.seek(res.offset)
                data = infile.read(res.size)
                with open("extracted/" + res.name, "wb") as outfile:
                    outfile.write(data)

    @staticmethod
    def extract_rd(path):
        """"Get list of resources from MEGAPEDE.RD."""
        MegapedeResource = namedtuple("MegapedeResource", ["size", "offset", "name"])
        resources = []
        with open(os.path.join(path, "MEGAPEDE.RD"), "rb") as rd:
            for line in rd:
                items = line.split()
                res = MegapedeResource(int(items[0]), int(items[1]), items[2].decode())
                resources.append(res)
        return resources
