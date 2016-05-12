import sys
import os
from optparse import SUPPRESS_HELP

import inkex
import object2path
import cspsubdiv
import cubicsuperpath
import inkex
import pathmodifier
import simplepath
import simplestyle
import simpletransform

from VC1520 import VC1520

__version__ = '1.0'
__author__ = 'Johan Van den Brande <johan@vandenbrande.com>'

class SendtoVC1520(object2path.ObjectToPath):
    def __init__(self):
        self.OptionParser.add_option('--active-tab', action = 'store', dest = 'active_tab', help=SUPPRESS_HELP)
        self.OptionParser.add_option('-d', '--device', action = 'store', dest = 'device', type = 'int', default = False, help='secondary device')
        self.OptionParser.add_option('-t', '--title', action = 'store', dest = 'title', type = 'string', default = False, help='title')

        self.flatness = 0.1
        self.global_dims = {
            'minX': None,
            'minY': None,
            'maxX': None,
            'maxY': None
        }

        object2path.ObjectToPath.__init__(self)

    def version(self):
        return __version__

    def author(self):
        return __author__

    def plot(self, title, objects, dims):
        plotter = VC1520(self.options.device)
        plotter.home()

        if title:
            plotter.lower_case(True)
            plotter.color('blue')
            plotter.size(1)
            plotter.puts("%s\r" % title)

        for object in objects:
            if object['color'] == (255,0,0):
                plotter.color('red')
            elif object['color'] == (0,255,0):
                plotter.color('green')
            elif object['color'] == (0,0,255):
                plotter.color('blue')
            else:
                plotter.color('black')

            lines = object['lines']
            first_point = lines[0]
            plotter.move(first_point[0], first_point[1])
            for point in lines:
                plotter.draw(point[0], point[1])

        plotter.move(0, dims['minY'])

    def path_to_lines(self, p):
        f = self.flatness
        is_flat = 0
        while is_flat < 1:
            try:
                cspsubdiv.cspsubdiv(p, f)
                is_flat = 1
            except IndexError:
                break
            except:
                f += 0.1
                if f > 2:
                    break
        lines = []
        for sub in p:
            for i in range(len(sub)):
                x = sub[i][1][0]
                y = sub[i][1][1]
                dims = self.global_dims
                if dims['minX'] is None or x < dims['minX']:
                    self.global_dims['minX'] = x
                elif dims['maxX'] is None or x > dims['maxX']:
                    self.global_dims['maxX'] = x
                if dims['minY'] is None or y < dims['minY']:
                    self.global_dims['minY'] = y
                elif dims['maxY'] is None or y > dims['maxY']:
                    self.global_dims['maxY'] = y
                lines.append([x,y])

        return lines

    def determine_dims(self, transformMatrix):
        # f = self.flatness
        # is_flat = 0
        # while is_flat < 1:
        #     try:
        #         cspsubdiv.cspsubdiv(p, f)
        #         is_flat = 1
        #     except IndexError:
        #         break
        #     except:
        #         f += 0.1
        #         if f > 2:
        #             break
        # for sub in p:
        #     for i in range(len(sub)):
        #         x = sub[i][1][0]
        #         y = sub[i][1][1]
        #         dims = self.global_dims
        #         if dims['minX'] is None or x < dims['minX']:
        #             self.global_dims['minX'] = x
        #         elif dims['maxX'] is None or x > dims['maxX']:
        #             self.global_dims['maxX'] = x
        #         if dims['minY'] is None or y < dims['minY']:
        #             self.global_dims['minY'] = y
        #         elif dims['maxY'] is None or y > dims['maxY']:
        #             self.global_dims['maxY'] = y
        minX = minY = maxX = maxY = None
        for [path, node] in self.processPaths(transformMatrix):
            for point in self.processPath(path):
                x = point[0]
                y = point[1]
                if minX is None or x < minX:
                    minX = x
                elif maxX is None or x > maxX:
                    maxX = x
                if minY is None or y < minY:
                    minY = y
                elif maxY is None or y > maxY:
                    maxY = y
        return [minX, minY, maxX, maxY]

    def processPaths(self, transformMatrix):
        path = '//svg:path'
        pm = pathmodifier.PathModifier()

        for node in self.document.getroot().xpath(path, namespaces=inkex.NSS):
            pm.objectToPath(node, True)
            d = node.get('d')
            p = cubicsuperpath.parsePath(d)
            t = node.get('transform')
            if t is not None:
                transformMatrix = simpletransform.composeTransform(transformMatrix, simpletransform.parseTransform(t))

            simpletransform.applyTransformToPath(transformMatrix, p)
            yield [p, node]

    def processPath(self, p):
        f = self.flatness
        is_flat = 0
        while is_flat < 1:
            try:
                cspsubdiv.cspsubdiv(p, f)
                is_flat = 1
            except IndexError:
                break
            except:
                f += 0.1
                if f > 2:
                    break
        for sub in p:
            for i in range(len(sub)):
                x = sub[i][1][0]
                y = sub[i][1][1]
                yield [x,y]

    def effect(self):
        #print >>self.tty, "Hello from VC1520"
        #print >>sys.stderr, "Hello from VC1520"
        #print >>sys.stderr, "Using secondary device: %d" % self.options.device

        object2path.ObjectToPath.effect(self)

        # print >>sys.stderr, "factor: %f" % self.calc_unit_factor()

        # doc_height = self.document.getroot().xpath(
        #     '@height', namespaces=inkex.NSS)[0]
        # try:
        #     h = self.unittouu(doc_height)
        # except AttributeError:  # Prior to Inkscape 0.91 fallback
        #     h = inkex.unittouu(doc_height)

        # doc_width = self.document.getroot().xpath(
        #     '@width', namespaces=inkex.NSS)[0]
        # try:
        #     w = self.unittouu(doc_width)
        # except AttributeError:  # Prior to Inkscape 0.91 fallback
        #    w = inkex.unittouu(doc_width)

        # Plot long side vertically as it is 900
        # matrix: [ x, y, offset ]

        #if w > h:
        #    print >>sys.stderr, "w > h"
        #    # rotate 90 degrees
        #    scale = 480.0 / h
        #    # scale and rotate
        #    # transformMatrix = [[0,-scale,0],[scale,0,0]]
        #    transformMatrix = simpletransform.parseTransform("scale(%f,%f)" % (scale, scale))
        #    # transformMatrix = simpletransform.composeTransform(transformMatrix, simpletransform.parseTransform("rotate(90)"))
        #else:
        #    print >>sys.stderr, "w <= h"
        #    # Width needs to 480
        #    scale = 480.0 / w
        #    # just scale
        #    transformMatrix = [[scale,0,240],[0,scale,240]]

        # scale = 480.0 / w
        # # transformMatrix = [[scale,0,0],[0,scale,0]]
        # print >>sys.stderr, "w: %f, h: %f, scale: %f" % (w, h, scale)

        # path = '//svg:path'
        # pm = pathmodifier.PathModifier()

        # for node in self.document.getroot().xpath(path, namespaces=inkex.NSS):
        #     pm.objectToPath(node, True)
        #     d = node.get('d')
        #     p = cubicsuperpath.parsePath(d)
        #     t = node.get('transform')
        #     if t is not None:
        #         m = simpletransform.parseTransform(t)
        #         simpletransform.applyTransformToPath(m, p)
        #     self.determine_dims(p)

        # # TODO: Check boundary for scaling: 480x999
        # #
        # scale = 480.0 / self.global_dims['maxX']
        # transformMatrix = [[scale,0,0],[0,scale,0]]
        # offsetX = scale * self.global_dims['maxX']
        # # offsetY = scale * self.global_dims['maxY']
        # offsetTransform = [[1,0,offsetX],[0,1,0]]

        # print >>sys.stderr, "w: %f, h: %f, scale: %f" % (self.global_dims['maxX'], self.global_dims['maxY'], scale)
        # objects = []
        # for node in self.document.getroot().xpath(path, namespaces=inkex.NSS):
        #     pm.objectToPath(node, True)
        #     d = node.get('d')
        #     color = (0, 0, 0)
        #     style = node.get('style')
        #     if style:
        #         style = simplestyle.parseStyle(style)
        #         if 'stroke' in style:
        #             if style['stroke'] and style['stroke'] != 'none':
        #                 color = simplestyle.parseColor(style['stroke'])

        #     p = cubicsuperpath.parsePath(d)

        #     t = node.get('transform')
        #     if t is not None:
        #         m = simpletransform.parseTransform(t)
        #         simpletransform.applyTransformToPath(m, p)

        #     #simpletransform.applyTransformToPath(transformMatrix, p)
        #     #rotate180 = [[-1,0,0],[0,-1,0]]
        #     #simpletransform.applyTransformToPath(rotate180, p)
            #simpletransform.applyTransformToPath(offsetTransform, p)

        #    lines = self.path_to_lines(p)

        #    objects.append({'color': color, 'lines': lines})

        # print >>sys.stderr, self.global_dims
        # f = open('out.txt', 'w')
        # print >>f, objects
        # f.close()
        # self.plot(self.options.title, objects, self.global_dims)
        #groupmat = [[self.mirrorX * self.scaleX * self.viewBoxTransformX, 0.0, 0.0], [0.0, self.mirrorY * self.scaleY * self.viewBoxTransformY, 0.0]]
        #groupmat = simpletransform.composeTransform(groupmat, simpletransform.parseTransform('rotate(' + self.options.orientation + ')'))

        transformMatrix = [[1,0,0],[0,1,0]]
        dims = self.determine_dims(transformMatrix)
        print >>sys.stderr, "HOI"
        print >>sys.stderr, dims

        [x,y,X,Y] = dims
        width = X - x
        height = Y - y

        # Longest side is vertical
        if width > height:
            scale = 480.0 / height
            print >>sys.stderr, "w > h, s: %f" % scale
            if scale * width > 999.0:
                # error
                return
            # rotate 90 degrees
            transformMatrix = [[1,0,-x],[0,1,-y]]
            transformMatrix = simpletransform.composeTransform(simpletransform.parseTransform('rotate(-90)'), transformMatrix)
            transformMatrix = simpletransform.composeTransform([[scale,0,0],[0,scale,0]], transformMatrix)
        else:
            scale = 480.0 / width
            print >>sys.stderr, "w <= h, s: %f" % scale
            if scale * height > 999.0:
                # error
                return
            transformMatrix = [[1,0,-x],[0,1,-y]]
            #   - rotate 180 degrees
            transformMatrix = simpletransform.composeTransform([[-1,0,0],[0,-1,0]], transformMatrix)
            #   - offset 480 X to the right
            transformMatrix = simpletransform.composeTransform([[1,0,width],[0,1,0]], transformMatrix)
            transformMatrix = simpletransform.composeTransform([[scale,0,0],[0,scale,0]], transformMatrix)

        print >>sys.stderr, "scale: %f" % scale
        print >>sys.stderr, transformMatrix
        paths = []
        for [path, node] in self.processPaths(transformMatrix):
            color = (0, 0, 0)
            style = node.get('style')
            if style:
                style = simplestyle.parseStyle(style)
                if 'stroke' in style:
                    if style['stroke'] and style['stroke'] != 'none':
                        color = simplestyle.parseColor(style['stroke'])
            points = []
            for point in self.processPath(path):
                points.append(point)
            paths.append({'color':color, 'points':points})

        dims = self.determine_dims(transformMatrix)
        print >>sys.stderr, "HOI 2"
        print >>sys.stderr, dims

        f = open('out.txt', 'w')
        print >>f, paths
        f.close()

    def getUnittouu(self, param):
        try:
            return inkex.unittouu(param)
        except AttributeError:
            return self.unittouu(param)

    def calc_unit_factor(self):
        """ return the scale factor for all dimension conversions.
            - The document units are always irrelevant as
              everything in inkscape is expected to be in 90dpi pixel units
        """
        # namedView = self.document.getroot().find(inkex.addNS('namedview', 'sodipodi'))
        # doc_units = self.getUnittouu(str(1.0) + namedView.get(inkex.addNS('document-units', 'inkscape')))
        # unit_factor = self.getUnittouu(str(1.0) + self.options.units)
        unit_factor = self.getUnittouu(str(1.0) + 'px')
        return unit_factor

if __name__ == '__main__':
        SendtoVC1520().affect()
        sys.exit(0)