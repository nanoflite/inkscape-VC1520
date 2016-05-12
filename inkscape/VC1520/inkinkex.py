#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

"""
Calls Inkscape from within an Inkscape extension.

Inkscape provides a lot of functionality which is usually unusable from within
a Python Inkscape extension. On the other hand, it is possible to script
Inkscape from the command line using the ``--verb``-option. This module
provides a replacement of the ``Effect`` class of the module ``inkex`` with a
new function ``call_inkscape`` which allows to call Inkscape from within an
extension which has been called by Inkscape. Besides this additional method,
this class works just like the usual ``Effect`` class.

The script attempts some guesswork to find out where the Inkscape executable
might be localized (a fact Inkscape doesn’t tell its extensions), but this is
rather brittle and might not work. If you encounter an
``InkscapeEnvironmentError``, or your extension fails to find the Inkscape
executable, uncomment the first line of code of the function
``_find_inkscape_path`` and provide a hardcoded path for your local Inkscape
executable.

Unfortunately, the ``--verb`` option is a bit of a hack and requires Inkscape
to start its GUI. If you try to speed things up by adding the option
``--without-gui``, things will stop working. Hopefully, one day Inkscape will
get a real scripting API, making this hack superfluous.


To write a lit of possible verbs into a file ``verblist.txt``, type

::

    inkscape --verb-list > verblist.txt

on the command line.

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
__date__ = "2011-01-24"
__version__ = "0.0.1"
__credits__ = """www.janthor.com"""
__docformat__ = "restructuredtext de"


import inkex
import inkutils

import os
import tempfile

from subprocess import Popen, PIPE


class InkEffect(inkex.Effect):

    def __init__(self):
        inkex.Effect.__init__(self)
        self.inkscape_path = inkutils.find_inkscape_path()

    def select_verb(self, id, verb, clause=True):
        if clause:
            return " --select=%s --verb=%s" % (id, verb)
        return ""

    def generate_commands(self, verbs, ids):
        if ids and isinstance(ids, str):
            return self.select_verb(ids, verbs)
        elif ids:
            return "".join([self.select_verb(id, verbs, id) for id in ids])
        elif isinstance(verbs, str):
            return " " + verbs
        else:
            return "".join([self.select_verb(i, v, i and v) for v, i in verbs])

    def call_inkscape(self, verbs, ids=None):
        """Calls Inkscape to perform inkscape operations on the document.

        Note that this destroys and recreates self.document, so any node
        you previously collected is no longer valid. Any manipulation you
        performed on self.document previous to calling ``call_inkscape``
        will be stored, but there is no use in searching for a particular
        node, calling ``call_inkscape`` and afterwards manipulating said node,
        since this node belongs to a document no longer valid. It *is* possible
        to store collections of id's, since those are more persistent between
        subsequent calls of ``call_inkscape``.

        Note also that ``call_inkscape`` is a rather costly operation: the
        current document is stored as a temporary file on disk, another
        Inkscape process is loaded into memory, this process loads, manipulates
        and saves the temporary file, and then this temporary file is read and
        parsed again to retrieve the DOM tree. It is therefore advisable to
        perform as much Inkscape commands in one go as possible.

        To perform an Inkscape command, you have to specify a *verb*, and an id
        of an object on which to perform this action. Both verbs and ids are
        strings. If you have just a single object with a single operation,
        you can specify both ``verbs`` and ``ids`` as a single string,
        respectively.

        If you have a bunch of objects on which you want to perform the same
        operation, you can specify ``verbs`` as a single string, and ``ids``
        as a list of strings.

        If you have a bunch of objects on which you have to perform a bunch of
        different operations, you can ommit ``ids`` and specify ``verbs`` as
        a list of (verb, id)-tuples.

        And finally, to give you the most ammount of flexibility imaginable,
        you can specify your own list of optional arguments to submit to
        Inkscape if you specify ``verbs`` as a single string and ommit ``ids``.

        Examples::

            def effect(self):
                # ...

                # Transform a single text element to a group of paths:
                self.call_inkscape("ObjectToPath", "text1234")

                # Transform several text elements into groups of paths:
                self.call_inkscape("ObjectToPath", ["text1", "text2", "text3"])

                # Perform several different operations:
                self.call_inkscape([("EditClone", "path1234"),
                                    ("ObjectToPath", "text5678")])

                # Do arbitrary stuff (remove unused definitions, duplicate
                # a text and convert the initial version to a path):
                self.call_inkscape(
                    "--vacuum-defs"
                    " --select=text1234 --verb=EditDuplicate"
                    " --verb=ObjectToPath")

                # ...
        """

        fd, tmp = tempfile.mkstemp(".svg", text=True)
        try:
            self.document.write(tmp)
            cmd = self.inkscape_path + " --file=\"%s\"" % tmp
            cmd += self.generate_commands(verbs, ids)
            cmd += " --verb=FileSave --verb=FileQuit"

            p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)

            rc = p.wait()
            out = p.stdout.read()
            err = p.stderr.read()

            self.parse(tmp)
            self.getposinlayer()
            self.getselected()
            self.getdocids()
        finally:
            os.close(fd)
            os.remove(tmp)
