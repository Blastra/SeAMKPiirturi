''' Module entry point for any other python program importing
    this folder.
    Date: 26 Oct 2016
    Author: Peter Scriven    
    Modified for SeAMK circumstances by: Pekka Heikkilä
    '''
import sys
import os

moduuliPolku = os.path.split(__file__)[0]

if moduuliPolku not in sys.path:
    sys.path.append(moduuliPolku)
    print("Moduulipolku "+str(moduuliPolku)+" lisätty")

from svg2gcode import generate_gcode, test

svgKuvaKansio = os.path.split(moduuliPolku)[0]

#kohdeSVG = sys.argv[1]
kohdeSVG = "SvgSuttu.svg"

generate_gcode(os.path.join(svgKuvaKansio, "static", kohdeSVG))


