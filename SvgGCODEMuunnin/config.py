''' Configuration file for SVG to GCODE converter
    Date: 26 Oct 2016
    Author: Peter Scriven
    Modified for SeAMK circumstances by: Pekka Heikkilä
'''


'''G-code emitted at the start of processing the SVG file'''
preamble = "M51\nG1 Z0.0\nG28"

'''G-code emitted at the end of processing the SVG file'''
postamble = "G28\nM50"

'''G-code emitted before processing a SVG shape'''
shape_preamble = "M51\nG4 P0.2"

'''G-code emitted after processing a SVG shape'''
shape_postamble = "G4 P0.2\nM51"

# A4 area:               210mm x 297mm

'''Print bed width in mm'''
bed_max_x = 1230 

'''Print bed height in mm'''
bed_max_y = 550

''' Used to control the smoothness/sharpness of the curves.
    Smaller the value greater the sharpness. Make sure the
    value is greater than 0.1'''
smoothness = 0.2
