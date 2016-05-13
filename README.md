# VC1520 plot extension for Inkscape.

![star](https://cloud.githubusercontent.com/assets/58341/15231097/68648a8c-1899-11e6-9504-1bdb688ba506.jpg)

With this extension, you can drive the VC1520 plotter from within Inkscape.

The extension converts the objects to a path in a temporary Inkscape window. Next it scales the drawing to fit within a 480 by 999 window for plotting.

If the width of the image is larger then the height, the drawing will rotate 90 degrees.

Ater installation, you can  find the extension under Extensions > Export > VC1520.

![inkscape](https://cloud.githubusercontent.com/assets/58341/15231096/686432b2-1899-11e6-809e-71d7b58e0dec.jpg)

There are a few options in the dialog:

  * You can choose the secondary address of the plotter, which in my case is 6, but normally is 4.
  * If you provide a title, you can also set the color of the title.
  * When you check the debug option, nothing will be plotted, but some info will be shown. If you plot a large object the debug output can get a bit sluggish.

If you want to plot in color, you have 4 to choose from: black, red, green and blue. Make sure that the color in the drawing is really red (255,0,0), green (0,255,0) or blue (0,0,255), otherwise black will be the result.

![armchair](https://cloud.githubusercontent.com/assets/58341/15231095/6862ad02-1899-11e6-860e-c655c89042d5.jpg)

## Install

Copy files to '~/.config/inkscape/extensions/'

## Dependencies

  * Inkscape
  * brew install opencbm
  * Working VC1520 plotter
  * xum1541 usb to IEC adapter

## Issues

  * Does not react on close, keeps on going when done.
  * Strange lines when converting some objects.
  * Probably a ton of other issues.

Cheers,
Johan


