# Classic Game Resource Reader (CGRR): Parse resources from classic games.
# Copyright (C) 2014  Tracy Poff
#
# This file is part of CGRR.
#
# CGRR is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# CGRR is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with CGRR.  If not, see <http://www.gnu.org/licenses/>.
"""Parses Megapede data."""
import logging
import os
import struct
from collections import namedtuple

import yapsy
from jinja2 import Environment, FileSystemLoader
from PIL import Image

import utilities
from errors import UnsupportedSoftwareException
from utilities import File, FileReader


env = Environment(loader=FileSystemLoader('./formats'))

class Megapede(yapsy.IPlugin.IPlugin):
    """Parses Megapede data."""

    key = "cheesy_megapede_a"
    title = "Megapede"
    developer = "Cheesy Software"
    description = "Megapede (Cheesy Software)"

    identifying_files = [
        [   # Megapede v1.2
            File("MEGAPEDE.EXE",  93328, "02b855b2afddfdec0fd7cda49d621106"),
            File("MEGACORE.EXE", 138407, "0f96f133ade66b5fb5e0f797d74a0863"),
        ],
        [   # Megapede v1.3c
            File("MEGAPEDE.EXE",  89844, "60de7f0f904c0edd86c6ac4069e109f6"),
            File("MEGACORE.EXE", 126448, "fce9aa8e9937211874efdbe8d88260be"),
        ],
        [   # Megapede v2.0c
            File("MEGAPEDE.EXE",  90182, "255a4201d87c369389749a4c8f2a3495"),
            File("MEGACORE.EXE", 161198, "37148f640b2cefb848ad58c2a564550b"),
        ],
    ]
    scorefile = "MEGAPEDE.SCO"

    # For details on the file format, see:
    #
    # https://bitbucket.org/sopoforic/cgrr/wiki/Megapede Score File Format
    score_reader = FileReader(
        format = [
            ("name", "10s"),
            ("padding", "x"), # Unknown meaning. Issue #1.
            ("score", "I"),
            ("level", "B"),
        ],
        massage_in = {
            "name" : (lambda s: s.decode('ascii').strip('\x00')),
        },
        massage_out = {
            "name" : (lambda s: s.encode('ascii')),
        },
    )

    @staticmethod
    def export(path, format="html"):
        """Export everything this class supports."""
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
        """Verify that the provided path is the supported game."""
        verified = any(
            [utilities.verify(identifying_files, path) for identifying_files
             in Megapede.identifying_files]
        )
        return verified

    @staticmethod
    def read_scores(path):
        """Return a list of scores."""
        scores = []
        with open(os.path.join(path, Megapede.scorefile), "rb") as scorefile:
            for data in iter(lambda: scorefile.read(Megapede.score_reader.struct.size), b""):
                scores.append(Megapede.score_reader.unpack(data))
        return scores

    @staticmethod
    def read_resources(path):
        """Return a dictionary containing resources from MEGAPEDE.RES.

        The dictionary maps file names to file contents.

        """
        resource_list = Megapede.read_rd(path)
        format = [
            (resource.name, "{}s".format(resource.size))
            for resource in sorted(resource_list, key=lambda r: r.offset)
        ]
        resource_reader = FileReader(format)
        resources = None
        with open(path + "MEGAPEDE.RES", "rb") as infile:
            resources = resource_reader.unpack(infile.read())
        return resources

    @staticmethod
    def read_rd(path):
        """"Return a list of resources from MEGAPEDE.RD."""
        # For details on the file format, see:
        #
        # https://bitbucket.org/sopoforic/cgrr/wiki/Megapede RD File Format
        MegapedeResource = namedtuple("MegapedeResource", ["size", "offset", "name"])
        resource_list = []
        if os.path.isfile(os.path.join(path, "MEGAPEDE.RD")):
            filepath = os.path.join(path, "MEGAPEDE.RD")  # v1.3c
        elif os.path.isfile(os.path.join(path, "MEGAPEDE.DIR")):
            filepath = os.path.join(path, "MEGAPEDE.DIR") # v1.2
        with open(filepath, "rb") as rd:
            for line in rd:
                items = line.split()
                res = MegapedeResource(int(items[0]), int(items[1]), items[2].decode())
                resource_list.append(res)
        return resource_list

    @staticmethod
    def read_palette(data):
        """Return a palette as a dictionary from color numbers to RGB values."""
        p = struct.unpack("768B", data)
        palette = list(zip(*[p[i::3] for i in range(3)]))
        return palette

    @staticmethod
    def read_image(image_data, palette_data):
        """Return an Image matching the input data."""
        (_, width, height) = struct.unpack("3B", image_data[:3])
        width *= 2
        height *= 2
        img = Image.new('RGB', (width, height))
        imgdata = struct.unpack("{}B".format(width*height), image_data[3:])
        palette = Megapede.read_palette(palette_data)
        pixmap = [palette[pixel] for pixel in imgdata]
        # There should no doubt be some gamma correction done, but I don't know
        # what value to use. 1.4 looks pretty close, but it's not perfect.
        # 
        # pixmap = [(int(pow(a,1.4)), int(pow(b,1.4)), int(pow(c,1.4))) for (a, b, c) in pixmap]
        img.putdata(pixmap)
        return img
