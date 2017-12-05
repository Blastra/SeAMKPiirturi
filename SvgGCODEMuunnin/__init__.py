''' Module entry point for any other python program importing
    this folder.
    Date: 26 Oct 2016
    Author: Peter Scriven    
    Modified for SeAMK circumstances by: Pekka Heikkilä
    '''
import sys
import os

moduuliPolku = os.getcwd()

if moduuliPolku not in sys.path:
    sys.path.append(moduuliPolku)
    print("Moduulipolku "+str(moduuliPolku)+" lisätty")

from svg2gcode import generate_gcode, test
#import svg2gcode

#kohdeSVG = sys.argv[0]
kohdeSVG = "SvgSuttu.svg"

generate_gcode(os.path.join(moduuliPolku, "MuunnettavatSVGt", kohdeSVG))


