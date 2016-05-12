import sys
from optparse import SUPPRESS_HELP

import inkex
import object2path
import cspsubdiv
import cubicsuperpath
import inkex
import pathmodifier
import simplestyle
from simpletransform import composeTransform, parseTransform, applyTransformToPath

from VC1520 import VC1520

__version__ = '1.0'
__author__ = 'Johan Van den Brande <johan@vandenbrande.com>'

inkex.localize()

class SendtoVC1520(object2path.ObjectToPath):
    def __init__(self):
        object2path.ObjectToPath.__init__(self)

        self.OptionParser.add_option('--active-tab', action = 'store', dest = 'active_tab', help=SUPPRESS_HELP)
        self.OptionParser.add_option('-d', '--device', action = 'store', dest = 'device', type = 'int', default = False, help='secondary device')
        self.OptionParser.add_option('-t', '--title', action = 'store', dest = 'title', type = 'string', default = False, help='title')
        self.OptionParser.add_option('-c', '--color', action='store', type='string', dest="color", default='black', help='title color')
        self.OptionParser.add_option('-x', '--debug', action='store', type='inkbool', dest='debug', default=False, help='debug')

    def version(self):
        return __version__

    def author(self):
        return __author__

    def find_color(self, color):
        if color == (255,0,0):
            return 'red'
        elif color == (0,255,0):
            return 'green'
        elif color == (0,0,255):
            return 'blue'
        else:
            return 'black'

    def plot(self, paths, minY):
        plotter = VC1520(self.options.device)
        plotter.home()

        if self.options.title:
            plotter.lower_case(True)
            plotter.color(self.options.color)
            plotter.size(1)
            plotter.puts("%s\r" % self.options.title)

        for path in paths:
            plotter.color(self.find_color(path['color']))
            points = path['points']
            plotter.move(points[0][0], points[0][1])
            for point in points:
                plotter.draw(point[0], point[1])

        plotter.move(0, minY)

    def determine_dims(self, transformMatrix):
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
                transformMatrix = composeTransform(transformMatrix, parseTransform(t))

            applyTransformToPath(transformMatrix, p)
            yield [p, node]

    def processPath(self, p):
        f = 0.1
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
        object2path.ObjectToPath.effect(self)

        transformMatrix = [[1,0,0],[0,1,0]]
        dims = self.determine_dims(transformMatrix)

        [x,y,X,Y] = dims
        width = X - x
        height = Y - y

        # Longest side is vertical
        if width > height:
            scale = 480.0 / height
            if scale * width > 999.0:
                inkex.errormsg("Plot area is to large (%f > 999)." % scale*height)
                exit()
            transformMatrix = parseTransform('translate(%f,%f)' % (-x,-y))
            transformMatrix = composeTransform(parseTransform('rotate(-90)'), transformMatrix)
            transformMatrix = composeTransform(parseTransform('scale(%f,%f)' % (scale,scale)), transformMatrix)
        else:
            scale = 480.0 / width
            if scale * height > 999.0:
                inkex.errormsg("Plot area is to large (%f > 999)." % scale*height)
                exit()
            transformMatrix = parseTransform('translate(%f,%f)' % (-x,-y))
            transformMatrix = composeTransform(parseTransform('rotate(180)'), transformMatrix)
            transformMatrix = composeTransform(parseTransform('translate(%f,0)' % width), transformMatrix)
            transformMatrix = composeTransform(parseTransform('scale(%f,%f)' % (scale,scale)), transformMatrix)

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
        if self.options.debug:
            print >>sys.stderr, "VC1520 debug info"
            print >>sys.stderr, "-----------------"
            print >>sys.stderr, "plot area: minX:%d, minY:%d, maxX:%d, maxY:%d" % tuple(dims)
            print >>sys.stderr, "nr paths: %d" % len(paths)
            i = 0
            print >>sys.stderr, "path;color;points"
            for path in paths:
                print >>sys.stderr, "%d;%s;%d" % (i,self.find_color(path['color']),len(path['points']))
                i += 1
            for path in paths:
                print >>sys.stderr, path
        else:
            self.plot(paths, dims[1])

if __name__ == '__main__':
        SendtoVC1520().affect()
        sys.exit(0)