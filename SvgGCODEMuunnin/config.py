''' Configuration file for SVG to GCODE converter
    Date: 26 Oct 2016
    Author: Peter Scriven
    Modified for SeAMK circumstances by: Pekka Heikkilä
'''


'''G-code emitted at the start of processing the SVG file'''
preamble = "F100000\nG90\nM51"

'''G-code emitted at the end of processing the SVG file'''
postamble = "M50\nM30"

'''G-code emitted before processing a SVG shape'''
shape_preamble = "M52"

'''G-code emitted after processing a SVG shape'''
shape_postamble = "\nM51"

# A4 area:               210mm x 297mm

#Print area coordinate limits actually 100 more for x and 50 for y,
#but limited area a bit for the sake of reliability.
'''Print bed width in mm'''
bed_max_x = 1130 

'''Print bed height in mm'''
bed_max_y = 500

''' Used to control the smoothness/sharpness of the curves.
    Smaller the value greater the sharpness. Make sure the
    value is greater than 0.1'''
smoothness = 0.2
