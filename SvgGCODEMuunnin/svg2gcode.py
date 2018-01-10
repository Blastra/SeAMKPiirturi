#!/usr/bin/env python

# External Imports
import os
import sys
import xml.etree.ElementTree as ET

# Local Imports
sys.path.insert(0, './lib') # (Import from lib folder)
import shapes as shapes_pkg
from shapes import point_generator
from config import *

import itertools as itr

DEBUGGING = True
SVG = set(['rect', 'circle', 'ellipse', 'line', 'polyline', 'polygon', 'path'])


def generate_gcode(filename):
    ''' The main method that converts svg files into gcode files.
        Still incomplete. See tests/start.svg'''

    # Check File Validity
    if not os.path.isfile(filename):
        raise ValueError("File "+filename+" not found.")

    if not filename.endswith('.svg'):
        raise ValueError("File "+filename+" is not an SVG file.")

    # Define the Output
    # ASSUMING LINUX / OSX FOLDER NAMING STYLE
    log = ""
    log += debug_log("Input File: "+filename)
    log += debug_log("Debug resides in: "+str(debug_log.__module__))

    #Define the file/folder paths to work with
    file = os.path.split(filename)[-1]
    dirlist = os.path.split(filename)[0]    
    dir_string = dirlist

    # Make Output File

    outdir = os.path.abspath(os.path.join(dirlist,"..","TuotetutNCTiedostot"))
    #outdir = os.path.join(dirlist,"gcode_output")
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    outfile = os.path.join(outdir, file.split(".svg")[0] + '.nc')
    log += debug_log("Output File: "+outfile)

    # Make Debug File
    #debugdir = os.path.join(dir_string, "log")
    debugdir = os.path.join(dirlist,"..","log")
    if not os.path.exists(debugdir):
        os.makedirs(debugdir)
    debug_file = os.path.join(debugdir, file.split(".svg")[0] + '.log')
    log += debug_log("Log File: "+debug_file+"\n")

    # Get the SVG Input File
    file = open(filename, 'r')
    tree = ET.parse(file)
    root = tree.getroot()
    print(dir(root))
    #print("Tree.getroot(): "+str(tree.getroot()+"\n"))
    file.close()
    
    # Get the Height and Width from the parent svg tag
    width = root.get('width')
    height = root.get('height')
    if width == None or height == None:
        viewbox = root.get('viewBox')
        if viewbox:
            _, _, width, height = viewbox.split()                

    if width == None or height == None:
        # raise ValueError("Unable to get width or height for the svg")
        print("Unable to get width and height for the svg")
        sys.exit(1)

    #print(type(width))
    
    # Scale the file appropriately
    # (Will never distort image - always scales evenly)
    # ASSUMES: Y ASIX IS LONG AXIS
    #          X AXIS IS SHORT AXIS
    # i.e. laser cutter is in "portrait"

    #Remove units so float conversion does not fail
    
    scale_x = bed_max_x / float(width.replace("mm",""))
    scale_y = bed_max_y / float(height.replace("mm",""))
    scale = min(scale_x, scale_y)
    if scale > 1:
        scale = 0.6


    log += debug_log("wdth: "+str(width))
    log += debug_log("hght: "+str(height))
    log += debug_log("scale: "+str(scale))
    log += debug_log("x%: "+str(scale_x))
    log += debug_log("y%: "+str(scale_y))

    # CREATE OUTPUT VARIABLE
    gcode = ""

    # Write Initial G-Codes
    gcode += preamble + "\n"
    
    # Iterate through svg elements

    commandStock = []
    
    for elem in root.iter():

        #gcode += "NIRNAR\n"
        log += debug_log("--Found Elem: "+str(elem))
        #new_shape = True
        
        
        try:
            tag_suffix = elem.tag.split("}")[-1]
        except:
            print("Error reading tag value:", tag_suffix)
            continue
        
        # Checks element is valid SVG shape
        if tag_suffix in SVG:

            log += debug_log("  --Name: "+str(tag_suffix))

            # Get corresponding class object from 'shapes.py'
            shape_class = getattr(shapes_pkg, tag_suffix)
            shape_obj = shape_class(elem)

            log += debug_log("\tClass : "+str(shape_class))
            log += debug_log("\tObject: "+str(shape_obj))
            log += debug_log("\tAttrs : "+str(list(elem.items())))
            log += debug_log("\tTransform: "+str(elem.get('transform')))


            ############ HERE'S THE MEAT!!! #############
            # Gets the Object path info in one of 2 ways:
            # 1. Reads the <tag>'s 'd' attribute.
            # 2. Reads the SVG and generates the path itself.
            d = shape_obj.d_path()
            
            log += debug_log("\td: "+str(d))

            # The *Transformation Matrix* #
            # Specifies something about how curves are approximated
            # Non-essential - a default is used if the method below
            #   returns None.

            m = shape_obj.transformation_matrix()
                        
            log += debug_log("\tm: "+str(m))

            if d:
                
                #print("type(d): "+str(type(d)))
                
                qir = str(d)

                highest_x = 0
                lowest_x = 0

                highest_y = 0
                lowest_y = 0

                #Split the chain of commands
                #where z appears, leaving the last
                #empty list out
                qirSplit = qir.split("z")[:-1]                
                
                #print("root.iter(): "+str(root.iter()))

                log += debug_log("\td is GOOD!")

                #gcode += shape_preamble + "\n"

                chkPoints = point_generator(d, m, smoothness)
                
                #Run a preliminary check of minimum and maximum
                #coordinates, then adjust accordingly to make
                #the lower left corner of the drawing
                #process be near the zero coordinates of
                #the drawing machine

                for x,y,cmdType in chkPoints:

                    #log += debug_log("\t  pt: "+str((x,y)))

                    #x = bed_max_x/2.0 - scale*x
                    #y = bed_max_y/2.0 - scale*y

                    x = scale*x
                    y = scale*y
                    
                    #y = bed_max_y - scale*y
                    if x > highest_x:
                        highest_x = x
                    if x < lowest_x:
                        lowest_x = x
                    if y > highest_y:
                        highest_y = y
                    if y < lowest_y:
                        lowest_y = y

                    #Store all bezier curve commands
                    #for counting and ending the
                    #drawing correctly
                    commandStock.append(cmdType)

                #Count the number of Z-commands
                zCounter = commandStock.count("Z")
                
                xAdj = 0
                yAdj = 0

                if lowest_x < 0:
                    xAdj = -lowest_x + 50
                if lowest_y < 0:
                    yAdj = -lowest_y + 30
                            
                points = point_generator(d, m, smoothness)              
                
                log += debug_log("\tPoints: "+str(points))

                #Generate the G-code

                new_shape = True

                #move_between_shapes = False

                #Count the finished shapes
                finishCounter = 0
                skipCounter = 0
                commandCount = 0
                    
                for x,y,cmdType in points:
                    
                    #log += debug_log("\t  pt: "+str((x,y)))

                    x = scale*x + xAdj
                    y = scale*y + yAdj

                    log += debug_log("\t  pt: "+str((x,y)))

                    #Check that the drawing board limits are not exceeded
                    if x >= 0 and x <= bed_max_x and y >= 0 and y <= bed_max_y:

                        #If the Z command is reached, increment the counter
                        #and close the shape with the point from which it was
                        #started
                        if cmdType == 'Z' and finishCounter < zCounter:
                            gcode += startPointStorage
                            new_shape = True
                            skipCounter = 3
                            finishCounter += 1

                        #If the number of commands matches the amount of commands
                        #given per shape, if the end is reached, lift the tool                        

                        if new_shape:
                            skipCounter -= 1
                            if skipCounter <= 0:
                                gcode += "M51\n"
                                startPointStorage = ("G00 X%0.1f Y%0.1f\n" % (x, y))
                                gcode += startPointStorage
                                gcode += "M52\n"
                                new_shape = False
                            
                        else:
                            gcode += ("G00 X%0.1f Y%0.1f\n" % (x, y))

                        commandCount += 1
                        
                        log += debug_log("\t    --Point printed")
                        
                    else:
                        log += debug_log("\t    --POINT NOT PRINTED ("+str(bed_max_x)+","+str(bed_max_y)+")")                        
                    
                gcode += shape_postamble + "\n"
                
            else:
                log += debug_log("\tNO PATH INSTRUCTIONS FOUND!!")
                
    else:
        log += debug_log("  --No Name: "+tag_suffix)

    
    gcode += postamble + "\n"

    print("highest_x: "+str(highest_x), "lowest_x: "+str(lowest_y),
          "highest_y: "+str(highest_y), "lowest_y: "+str(lowest_y))
    
    # Write the Result
    ofile = open(outfile, 'w+')
    ofile.write(gcode)
    ofile.close()

    # Write Debugging
    if DEBUGGING:
        dfile = open(debug_file, 'w+')
        dfile.write(log)
        dfile.close()



def debug_log(message):
    ''' Simple debugging function. If you don't understand 
        something then chuck this frickin everywhere. '''
    if (DEBUGGING):
        print(message)
    return message+'\n'



def test(filename):
    ''' Simple test function to call to check that this 
        module has been loaded properly'''
    circle_gcode = "G28\nG01 Z5.0\nG4 P200\nG01 X10.0 Y100.0\nG01 X10.0 Y101.8\nG01 X10.6 Y107.0\nG01 X11.8 Y112.1\nG01 X13.7 Y117.0\nG01 X16.2 Y121.5\nG01 X19.3 Y125.7\nG01 X22.9 Y129.5\nG01 X27.0 Y132.8\nG01 X31.5 Y135.5\nG01 X36.4 Y137.7\nG01 X41.4 Y139.1\nG01 X46.5 Y139.9\nG01 X51.7 Y140.0\nG01 X56.9 Y139.4\nG01 X62.0 Y138.2\nG01 X66.9 Y136.3\nG01 X71.5 Y133.7\nG01 X75.8 Y130.6\nG01 X79.6 Y127.0\nG01 X82.8 Y122.9\nG01 X85.5 Y118.5\nG01 X87.6 Y113.8\nG01 X89.1 Y108.8\nG01 X89.9 Y103.6\nG01 X90.0 Y98.2\nG01 X89.4 Y93.0\nG01 X88.2 Y87.9\nG01 X86.3 Y83.0\nG01 X83.8 Y78.5\nG01 X80.7 Y74.3\nG01 X77.1 Y70.5\nG01 X73.0 Y67.2\nG01 X68.5 Y64.5\nG01 X63.6 Y62.3\nG01 X58.6 Y60.9\nG01 X53.5 Y60.1\nG01 X48.3 Y60.0\nG01 X43.1 Y60.6\nG01 X38.0 Y61.8\nG01 X33.1 Y63.7\nG01 X28.5 Y66.3\nG01 X24.2 Y69.4\nG01 X20.4 Y73.0\nG01 X17.2 Y77.1\nG01 X14.5 Y81.5\nG01 X12.4 Y86.2\nG01 X10.9 Y91.2\nG01 X10.1 Y96.4\nG01 X10.0 Y100.0\nG4 P200\nG4 P200\nG01 X110.0 Y100.0\nG01 X110.0 Y101.8\nG01 X110.6 Y107.0\nG01 X111.8 Y112.1\nG01 X113.7 Y117.0\nG01 X116.2 Y121.5\nG01 X119.3 Y125.7\nG01 X122.9 Y129.5\nG01 X127.0 Y132.8\nG01 X131.5 Y135.5\nG01 X136.4 Y137.7\nG01 X141.4 Y139.1\nG01 X146.5 Y139.9\nG01 X151.7 Y140.0\nG01 X156.9 Y139.4\nG01 X162.0 Y138.2\nG01 X166.9 Y136.3\nG01 X171.5 Y133.7\nG01 X175.8 Y130.6\nG01 X179.6 Y127.0\nG01 X182.8 Y122.9\nG01 X185.5 Y118.5\nG01 X187.6 Y113.8\nG01 X189.1 Y108.8\nG01 X189.9 Y103.6\nG01 X190.0 Y98.2\nG01 X189.4 Y93.0\nG01 X188.2 Y87.9\nG01 X186.3 Y83.0\nG01 X183.8 Y78.5\nG01 X180.7 Y74.3\nG01 X177.1 Y70.5\nG01 X173.0 Y67.2\nG01 X168.5 Y64.5\nG01 X163.6 Y62.3\nG01 X158.6 Y60.9\nG01 X153.5 Y60.1\nG01 X148.3 Y60.0\nG01 X143.1 Y60.6\nG01 X138.0 Y61.8\nG01 X133.1 Y63.7\nG01 X128.5 Y66.3\nG01 X124.2 Y69.4\nG01 X120.4 Y73.0\nG01 X117.2 Y77.1\nG01 X114.5 Y81.5\nG01 X112.4 Y86.2\nG01 X110.9 Y91.2\nG01 X110.1 Y96.4\nG01 X110.0 Y100.0\nG4 P200\nG28\n"
    print(circle_gcode[:90], "...")
    return circle_gcode



if __name__ == "__main__":
    ''' If this file is called by itself in the command line
        then this will execute.'''
    file = input("Please supply a filename: ")
    #generate_gcode(file)
    
