#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

"""
Converts objects to paths

The extension converts all objects in the current layer into paths

To convert objects to paths, Inkscape itself is called from within this
extension, using the ``--verb`` hack provided by the ``inkinkex`` module. The
restrictions of the ``inkinkex`` module are inherited by this extension.

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""

__author__ = "Jan Thor, Brad Pitcher"
__date__ = "2011-01-26"
__version__ = "0.0.1"
__credits__ = """http://www.janthor.com"""
__docformat__ = "restructuredtext de"

import inkinkex
import inkex
import re


S = "{http://www.w3.org/2000/svg}"
nsmap = {"svg": "http://www.w3.org/2000/svg"}


class ObjectToPath(inkinkex.InkEffect):
    def effect(self):
        objects = []
        # Collect objects
        for node in self.current_layer.iterdescendants():
            objects.append(node.get("id"))
        # Convert objects to paths
        self.call_inkscape("ObjectToPath", objects)


if __name__ == '__main__':
    ObjectToPath().affect()
