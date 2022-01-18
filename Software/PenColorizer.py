import re #To perform the search and replace.

try:
    from ..Script import Script
    runsStandalone = False
except:
    from typing import Optional, Any, Dict, TYPE_CHECKING, List
    import collections
    import json
    import sys

    class Script(object):
        def injectSettingData(self, jsonString):
            self._settingObj = json.loads(jsonString)

        def getSettingDataString(self):
            return "";

        def getSettingValueByKey(self, key: str) -> Any:
            try:
                return self._settingObj[key]
            except:
                pass
            if not '_defaultSettingsObj' in dir(self):
                self._defaultSettingObj = json.loads(self.getSettingDataString())
            return self._defaultSettingObj["settings"][key]["default_value"]

    runsStandalone = True

class PenColorizer(Script):
    """Performs a search-and-replace on all g-code.
    Due to technical limitations, the search can't cross the border between
    layers.
    """

    def getSettingDataString(self):
        return """{
            "name": "PenColorizer",
            "key": "PenColorizer",
            "metadata": {},
            "version": 2,
            "settings":
            {
                "PenXOffset":
                {
                    "label": "Pen X Offset",
                    "description": "Offset of your pen in X direction",
                    "type": "float",
                    "default_value": 36.1
                },
                "PenYOffset":
                {
                    "label": "Pen Y Offset",
                    "description": "Offset of your pen in Y direction",
                    "type": "float",
                    "default_value": 45.8
                },
                "PenZOffset":
                {
                    "label": "Pen Z Offset",
                    "description": "Offset of your pen in Z direction",
                    "type": "float",
                    "default_value": 3.2
                },
                "FirstPenXPosition":
                {
                    "label": "First Pen X Position",
                    "description": "X position for holding the first pen in the pen rack",
                    "type": "float",
                    "default_value": 28.0
                },
                "FirstPenZPosition":
                {
                    "label": "First Pen Z Position",
                    "description": "Z position for holding the first pen in the pen rack",
                    "type": "float",
                    "default_value": 238.0
                },
                "ExtraRetraction":
                {
                    "label": "Retraction during painting",
                    "description": "Extra amount of retraction during painting",
                    "type": "float",
                    "default_value": 5.5
                },
                "Interlace":
                {
                    "label": "Interlace colors",
                    "description": "Only paint every second layer",
                    "type": "bool",
                    "default_value": true
                }
            }
        }"""

    global getCoord
    def getCoord(gcode, params):
        return re.findall(r'([' + params + '][+-]?[0-9]*[.]?[0-9]+)', gcode)

    global getValue
    def getValue(coord, param):
        return next((float(i[1:]) for i in coord if i.startswith(param)), None)

    def getPen(self, pen):    
        penside = pen % 2
        penoffset = float(int(pen / 2)) * 68.0
        
        if penside == 0:
            getlines = ["; get pen " + str(pen+1),
                        "G0 F" + str(self.speedTravelFast) + " ; set speed fast",
                        "G0 X" + str(self.penstartx + penoffset) + " Z" + str(self.penstarty - 152.0) + " ; go under pen",
                        "G0 F" + str(self.speedTravelSlow) + " ; set speed slow",
                        "G0 X" + str(self.penstartx + penoffset) + " Z" + str(self.penstarty) + " ; lift pen",
                        "G0 X" + str(self.penstartx + 20.5 + penoffset) + " Z" + str(self.penstarty) + " ; move pen right",
                        "G0 F" + str(self.speedTravelFast) + " ; set speed fast",
                        "G0 X" + str(self.penstartx + 20.5 + penoffset) + " Z" + str(self.penstarty - 152.0) + " ; lower pen"]
        else:
            getlines = ["; get pen " + str(pen+1),
                        "G0 F" + str(self.speedTravelFast) + " ; set speed fast",
                        "G0 X" + str(self.penstartx + 41.0 + penoffset) + " Z" + str(self.penstarty - 152.0) + " ; go under pen",
                        "G0 F" + str(self.speedTravelSlow) + " ; set speed slow",
                        "G0 X" + str(self.penstartx + 41.0 + penoffset) + " Z" + str(self.penstarty) + " ; lift pen",
                        "G0 X" + str(self.penstartx + 20.5 + penoffset) + " Z" + str(self.penstarty) + " ; move pen right",
                        "G0 F" + str(self.speedTravelFast) + " ; set speed fast",
                        "G0 X" + str(self.penstartx + 20.5 + penoffset) + " Z" + str(self.penstarty - 152.0) + " ; lower pen"]

        getlines[1:1] = [ "M203 Z" + str(self.feedrateZFast) + " ; sets faster z max feedrate" ]
        getlines.append(  "M203 Z" + str(self.feedrateZSlow) + " ; restore z max feedrate")

        return getlines
        
    def putPen(self, pen):
        penside = pen % 2
        penoffset = float(int(pen / 2)) * 68.0
        
        if penside == 0:
            putlines = ["; put pen " + str(pen+1),
                        "G0 F" + str(self.speedTravelFast) + " ; set speed fast",
                        "G0 X" + str(self.penstartx + 20.5 + penoffset) + " Z" + str(self.penstarty - 152.0) + " ; go under pen",
                        "G0 X" + str(self.penstartx + 20.5 + penoffset) + " Z" + str(self.penstarty) + " ; lift pen",
                        "G0 F" + str(self.speedTravelSlow) + " ; set speed slow",
                        "G0 X" + str(self.penstartx + penoffset) + " Z" + str(self.penstarty) + " ; move pen left",
                        "G0 X" + str(self.penstartx + penoffset) + " Z" + str(self.penstarty - 152.0) + " ; lower pen",
                        "G0 F" + str(self.speedTravelFast) + " ; set speed fast", ""]
        else:
            putlines = ["; put pen " + str(pen+1),
                        "G0 F" + str(self.speedTravelFast) + " ; set speed fast",
                        "G0 X" + str(self.penstartx + 20.5 + penoffset) + " Z" + str(self.penstarty - 152.0) + " ; go under pen",
                        "G0 X" + str(self.penstartx + 20.5 + penoffset) + " Z" + str(self.penstarty) + " ; lift pen",
                        "G0 F" + str(self.speedTravelSlow) + " ; set speed slow",
                        "G0 X" + str(self.penstartx + 41.0 + penoffset) + " Z" + str(self.penstarty) + " ; move pen left",
                        "G0 X" + str(self.penstartx + 41.0 + penoffset) + " Z" + str(self.penstarty - 152.0) + " ; lower pen",
                        "G0 F" + str(self.speedTravelFast) + " ; set speed fast", ""]

        putlines[1:1] = [ "M203 Z" + str(self.feedrateZFast) + " ; sets faster z max feedrate" ]
        putlines.append(  "M203 Z" + str(self.feedrateZSlow) + " ; restore z max feedrate")

        return putlines

    def offset(self, gcode, zoffset):
        coord = getCoord(gcode, "FXYZ")
        newgcode = gcode[:2]
        
        F = getValue(coord, "F")
        if F != None:
            newgcode += " " + "F3600"#F
            
        X = getValue(coord, "X")
        if X != None:
            newgcode += " X" + "{:0.3f}".format(X + self.xoffset)
            
        Y = getValue(coord, "Y")
        if Y != None:
            newgcode += " Y" + "{:0.3f}".format(Y + self.yoffset)
            
        Z = getValue(coord, "Z")
        if Z != None:
            newgcode += " Z" + "{:0.3f}".format(Z + self.zoffset + zoffset)
        
        return newgcode

    def lift(self, gcode, zoffset):
        coord = re.findall(r'[XYZF].?\d+(?:.\d+)?', gcode)
        newgcode = gcode[:2]
        
        F = next((i for i in coord if i.startswith('F')), None)
        if F != None:
            newgcode += " " + F
            
        X = next((i for i in coord if i.startswith('X')), None)
        if X != None:
            newgcode += " X" + "{:0.3f}".format((float(X[1:])))
            
        Y = next((i for i in coord if i.startswith('Y')), None)
        if Y != None:
            newgcode += " Y" + "{:0.3f}".format((float(Y[1:])))
            
        Z = next((i for i in coord if i.startswith('Z')), None)
        if Z != None:
            newgcode += " Z" + "{:0.3f}".format((float(Z[1:]) + zoffset))
        
        return newgcode
        
    def getFirstPos(self, lines):
        for line in lines:
            if "G0" in line or "G1" in line:
                coord = re.findall(r'[XYZ].?\d+(?:.\d+)?', line)
                
                X = next((i for i in coord if i.startswith('X')), None)
                Y = next((i for i in coord if i.startswith('Y')), None)
                Z = next((i for i in coord if i.startswith('Z')), None)
                
                if X != None and Y != None and Z != None:
                    return line
                
        return "; nothing found"
    
    def addExplicitZ(self, line):
        parts = line.partition(";")

        newline = parts[0]

        if bool(newline.strip()) == False:
            return line
            
        coord = getCoord(line, "Z")
        Z = getValue(coord, "Z")
        if Z == None:
            newline += " Z" + "{:0.3f}".format(self.lastZ)

        return "".join([newline, parts[1], parts[2]])

    def __init__(self):
        self.layerPartMarker = ";LAYER:"
        self.typePattern = re.compile(r'^;TYPE:(.*)')
        self.typePrimeTowerMarker = "PRIME-TOWER"
        self.typeIncludedMarkers = ["WALL-INNER", "WALL-OUTER"]
        self.speedTravelFast = 10800
        self.speedTravelSlow = 2000
        self.feedrateZFast = 30
        self.feedrateZSlow = 12
        
    def execute(self, data):
    
        self.penstartx = self.getSettingValueByKey("FirstPenXPosition")# 28.0
        self.penstarty = self.getSettingValueByKey("FirstPenZPosition")#238.0
    
        self.xoffset = self.getSettingValueByKey("PenXOffset")#36.1
        self.yoffset = self.getSettingValueByKey("PenYOffset")#45.3
        self.zoffset = self.getSettingValueByKey("PenZOffset")#3.2
        self.lastZ = 0.2
        layerheight = 0.2
        
        lastlayerx = 100.0
        lastlayery = 100.0
        lastlayerz = 0.3
        
        drawrectract = self.getSettingValueByKey("ExtraRetraction")
        interlace = self.getSettingValueByKey("Interlace")
        
        isRetractMove = True

        layer_counter = -1
        #iterate layers
        curT = 0
        for layer_number, layer in enumerate(data):
            lines = layer.split("\n")
            #lines = self.addExplicitZ(lines)
            
            newlines = []
            isLayer = lines[0].startswith(self.layerPartMarker)

            if isLayer:
                layer_counter += 1

            #get pen & set height
            #zheight = layerheight * (layer_number - 1)
            
            #setup drawbuffers
            drawlines = [None] * 8
            drawlinesHasData = [False] * 8
            for i in range(8):
                drawlines[i] = ["; draw color " + str(i+1)]
            
            isPrimeTower = False
            primelines = ["; moved prime tower"]

            shouldBeDrawn = False
            
            linestoskip = 0
            
            zhopOffset = 3.0
            
            wasG0move = False
            
            #iterate lines
            for line in lines:
                if linestoskip > 0:
                    linestoskip -= 1
                    continue
            
                if ";Layer height:" in line:
                    layerheight = float(line[14:])
                    newlines.append(line)
                    continue

                #type change
                m = self.typePattern.search(line)
                if m:
                    if m.groups(0)[0] == self.typePrimeTowerMarker:
                        isPrimeTower = True
                        shouldBeDrawn = False
                    elif next((em for em in self.typeIncludedMarkers if m.groups(0)[0] == em), None) != None:
                        if(curT > 0):
                            drawlines[curT - 1].append("; drawing type: " + m.groups(0)[0])
                        shouldBeDrawn = True
                        isPrimeTower = False
                    else:
                        shouldBeDrawn = False
                        isPrimeTower = False
                    
                    newlines.append(line)
                    continue
            
                #offset G1 codes & remember curZ
                if "G0" in line or "G1" in line:
                    coord = getCoord(line, "XYZEF")

                    Z = getValue(coord, "Z")
                    if Z != None:
                        self.lastZ = Z
                
                    #should we draw?
                    draw = curT > 0 and layer_counter >= 0 and shouldBeDrawn == True and isPrimeTower == False and ((layer_counter + curT) % 2 == 0 or interlace == False)
                
                    #retract move?
                    E = getValue(coord, "E")
                    if E != None:
                        if E < 0.0: 
                            isRetractMove = True
                            zhopOffset = 3.0 
                        else:
                            isRetractMove = False
                            zhopOffset = 0.0
                            
                    '''#G0 Move?
                    if "G0" in line:
                        zhopOffset = 3.0
                        
                        if wasG0move == False and draw == True: #we transition to G0 Move
                            drawlines[curT].append(self.offset(line, 0.0))
                    
                        wasG0move = True
                    else:
                        zhopOffset = 0.0 
                        
                        if wasG0move == True and draw == True: #we transition from G0 Move
                            drawlines[curT].append(self.offset(line, 3.0))
                        
                        wasG0move = False'''
                    
                
                    if draw == True:
                        drawlinesHasData[curT - 1] = True
                        drawlines[curT - 1].append(self.offset(self.addExplicitZ(line), zhopOffset))
                       
                    if isPrimeTower:
                        primelines.append(line)
                    else:
                        newlines.append(line)
                        
                    #remember last pos
                    
                    X = next((i for i in coord if i.startswith('X')), None)
                    if X != None:
                        lastlayerx = float(X[1:])
                        
                    Y = next((i for i in coord if i.startswith('Y')), None)
                    if Y != None:
                        lastlayery = float(Y[1:])
                        
                    Z = next((i for i in coord if i.startswith('Z')), None)
                    if Z != None:
                        lastlayerz = float(Z[1:])

                    continue
                                            
                #filter out all dual extruder related gcodes but log which extruder should be active right now
                if re.match(r'^T[0-8]', line):
                    curT = int(line[1:2])
                    newlines.append(";" + line)
                    continue
                
                #filter out extruder related commands
                if re.search(r'T[1-8](\s|$)', line):
                    newlines.append(";" + line)
                    continue

                #filter out extruder heating commands
                #elif "M109" in line and isLayer:
                #     newlines.append(";" + line)
                #elif "M104" in line and isLayer:
                #     newlines.append(";" + line)
                #elif "M105" in line and isLayer:
                #     newlines.append(";" + line)

                # just append the new line if we do not need to alter it
                newlines.append(line)

            #move prime tower to layer startswith
            #primelines.append(";end prime tower")
            #if len(primelines) > 3:
            #    newlines[2:2] = primelines
            print()
            #add drawlines
            if isLayer and next((l for l in drawlinesHasData if l == True), None) != None:
                newlines += " ; start drawing"
                newlines += ["G1 F1500 E-" + str(drawrectract) + " ; retract before drawing"] #retract before drawing
                
                for i in range(8):
                    if drawlinesHasData[i] == False:
                        continue
                        
                    drawlines[i][1:1] = [self.lift(self.getFirstPos(drawlines[i]), 3.0) + " ; lower pen from above the first spot"] # lower pen from above the first spot
                    drawlines[i][1:1] = self.getPen(i)
                    drawlines[i] += [self.lift(drawlines[i][-1], 3.0) + " ; raise pen from the last spot"] # raise pen from the last spot
                    drawlines[i] += self.putPen(i)

                    newlines += drawlines[i]
                
                #prime after drawing
                newlines += ["G0 X" + str(lastlayerx) + " Y" + str(lastlayery) + " Z" + str(lastlayerz + 2.0), 
                    "G0 X" + str(lastlayerx) + " Y" + str(lastlayery) + " Z" + str(lastlayerz) + " ; return to last pos after drawing"]
                newlines += ["G1 F1500 E" + str(drawrectract), " ; unretract after drawing"]

            result = "\n".join(newlines)
            data[layer_number] = result

        return data

# run this if not executed via Cura
if runsStandalone == True:
    import argparse

    parser = argparse.ArgumentParser(description='Postprocess gcode file to add colors using pens.', exit_on_error=True)
    parser.add_argument('-c', '--config', help='path to the config json file.', required=False)
    parser.add_argument('-i', '--input', help='path to the input gcode file.', required=True)
    parser.add_argument('-o', '--output', help='path to the output gcode file. note: will be overwritten if it already exists.', required=False)
    parser.add_argument('--overwrite', help='overwrites the original file if set. if not set, a .processed.gcode file will be created (and overwritten if existent). ignored when output is set.', default=False, required=False, action='store_true')

    args = parser.parse_args()

    configFilename = args.config
    inputFilename = args.input
    outputFilename = args.output
    overwriteFile = args.overwrite

#    inputFilename = str(getenv('SLIC3R_PP_OUTPUT_NAME'))

    # create script instance
    script = PenColorizer()

    # read config
    hasConfig = False
    try:
        print("Reading config from " + configFilename);
        with open(configFilename, "r") as file:
            script.injectSettingData(file.read())
        hasConfig = True
    except FileNotFoundError:
        print("Config not found, falling back to defaults!")
    except BaseException as e:
        print("Error reading config: " + str(e))

    if hasConfig == False:
        print("### Defaults will most likely not work for your printer and can damage your machine! ###")
        input("Press Enter to continue anyway...")

    # Cura
    #partStartDelimiters = [";LAYER:", ";Generated with"]
    #partEndDelimiters = [";TIME_ELAPSED"]
    #script.layerPartMarker = ";LAYER:"
    #script.typeExcludedMarkers = 

    # PrusaSlicer
    partStartDelimiters = [";LAYER_CHANGE", "; generated by "]
    partEndDelimiters = [";TYPE:Custom"]
    script.layerPartMarker = ";LAYER_CHANGE"
    script.typeIncludedMarkers = ["Top solid infill", "Perimeter", "External perimeter", "Solid infill"]
    
    # read input gcode file
    print("Running script on " + inputFilename)
    with open(inputFilename) as file:
        lines = file.readlines()

    filePartsLineBuffers = []
    lineBuffer = []
    for i in range(0, len(lines)):
        line = lines[i]

        # check if a part starts here
        # parts are layers and other file parts defined by cura, e.g. the comment block at the beginning and the start gcode sequence
        isPartStart = next((l for l in partStartDelimiters if line.startswith(l)), None) != None
        isPartEnd = next((l for l in partEndDelimiters if line.startswith(l)), None) != None

        if isPartStart or isPartEnd:
            if isPartEnd:
                lineBuffer.append(line)
            if len(lineBuffer) > 0:
                filePartsLineBuffers.append(lineBuffer.copy())
                lineBuffer.clear()

        if not isPartEnd:
            lineBuffer.append(line)
    
    if len(lineBuffer) > 0:
        filePartsLineBuffers.append(lineBuffer.copy())

    # add comment stating this file was postprocessed
    filePartsLineBuffers[0].insert(len(filePartsLineBuffers[0]), ";POSTPROCESSED\n")

    # split fist line of last layer to its own layer so we conform with whatever cura does
    lastFilePartLineBuffer = filePartsLineBuffers[len(filePartsLineBuffers)-1].copy();
    filePartsLineBuffers[len(filePartsLineBuffers)-1] = [lastFilePartLineBuffer[0]]
    lastFilePartLineBuffer.remove(lastFilePartLineBuffer[0])
    filePartsLineBuffers.append(lastFilePartLineBuffer)

    # merge layer lines to string
    layers = []
    for i in range(0, len(filePartsLineBuffers)):
        layers.append("".join(filePartsLineBuffers[i]))


    # execute script
    layers = script.execute(layers)

    # write output gcode file
    if outputFilename == None:
        if overwriteFile:
            outputFilename = inputFilename
        else:
            outputFilename = inputFilename.partition(".gcode")[0] + ".processed.gcode"

    print("Writing processed file to " + outputFilename);
    with open(outputFilename, "w", newline='') as file:
        for i in range(0, len(layers)):
            file.write(layers[i])