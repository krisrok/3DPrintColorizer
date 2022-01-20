import re

try:
    # first tries to run as Cura's postprocessing script
    from ..Script import Script
    runsStandalone = False
except:
    # otherwise we have to construct a base class for compatibility
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

isVerbose = False

class PenColorizer(Script):

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
    def getValue(coord, param, defaultValue = None):
        return next((float(i[1:]) for i in coord if i.startswith(param)), defaultValue)

    global verbosePrint
    verbosePrint = lambda msg: None

    def getPen(self, pen):    
        penside = pen % 2
        penoffset = float(int(pen / 2)) * 68.0
        
        if penside == 0:
            getlines = ["; get pen " + str(pen+1),
                        "G0 F{} X{:0.3f} Z{:0.3f}".format(self.speedTravelFast, self.firstPenInRackPositionX + penoffset, self.firstPenInRackPositionZ - 152.0) + " ; go under pen",
                        "G0 F{} X{:0.3f} Z{:0.3f}".format(self.speedTravelSlow, self.firstPenInRackPositionX + penoffset, self.firstPenInRackPositionZ) + " ; lift pen",
                        "G0 F{} X{:0.3f} Z{:0.3f}".format(self.speedTravelSlow, self.firstPenInRackPositionX + penoffset + 20.5, self.firstPenInRackPositionZ) + " ; move pen right",
                        "G0 F{} X{:0.3f} Z{:0.3f}".format(self.speedTravelFast, self.firstPenInRackPositionX + penoffset + 20.5, self.firstPenInRackPositionZ - 152.0) + " ; lower pen "]
        else:
            getlines = ["; get pen " + str(pen+1),
                        "G0 F{} X{:0.3f} Z{:0.3f}".format(self.speedTravelFast, self.firstPenInRackPositionX + penoffset + 41.0, self.firstPenInRackPositionZ - 152.0) + " ; go under pen",
                        "G0 F{} X{:0.3f} Z{:0.3f}".format(self.speedTravelSlow, self.firstPenInRackPositionX + penoffset + 41.0, self.firstPenInRackPositionZ) + " ; lift pen",
                        "G0 F{} X{:0.3f} Z{:0.3f}".format(self.speedTravelSlow, self.firstPenInRackPositionX + penoffset + 20.5, self.firstPenInRackPositionZ) + " ; move pen left",
                        "G0 F{} X{:0.3f} Z{:0.3f}".format(self.speedTravelFast, self.firstPenInRackPositionX + penoffset + 20.5, self.firstPenInRackPositionZ - 152.0) + " ; lower pen "]

        getlines[1:1] = [ "M203 Z" + str(self.maxFeedrateZFast) + " ; sets faster z max feedrate" ]
        getlines.append(  "M203 Z" + str(self.maxFeedrateZSlow) + " ; restore z max feedrate")

        return getlines
        
    def putPen(self, pen):
        penside = pen % 2
        penoffset = float(int(pen / 2)) * 68.0
        
        if penside == 0:
            putlines = ["; put pen " + str(pen+1),
                        "G0 F{} X{:0.3f} Z{:0.3f}".format(self.speedTravelFast, self.firstPenInRackPositionX + penoffset + 20.5, self.firstPenInRackPositionZ - 152.0) + " ; !lower pen ",
                        "G0 F{} X{:0.3f} Z{:0.3f}".format(self.speedTravelSlow, self.firstPenInRackPositionX + penoffset + 20.5, self.firstPenInRackPositionZ) + " ; !move pen right",
                        "G0 F{} X{:0.3f} Z{:0.3f}".format(self.speedTravelSlow, self.firstPenInRackPositionX + penoffset, self.firstPenInRackPositionZ) + " ; !lift pen",
                        "G0 F{} X{:0.3f} Z{:0.3f}".format(self.speedTravelFast, self.firstPenInRackPositionX + penoffset, self.firstPenInRackPositionZ - 152.0) + " ; !go under pen"]
        else:
            putlines = ["; put pen " + str(pen+1),
                        "G0 F{} X{:0.3f} Z{:0.3f}".format(self.speedTravelFast, self.firstPenInRackPositionX + penoffset + 20.5, self.firstPenInRackPositionZ - 152.0) + " ; !lower pen ",
                        "G0 F{} X{:0.3f} Z{:0.3f}".format(self.speedTravelSlow, self.firstPenInRackPositionX + penoffset + 20.5, self.firstPenInRackPositionZ) + " ; !move pen right",
                        "G0 F{} X{:0.3f} Z{:0.3f}".format(self.speedTravelSlow, self.firstPenInRackPositionX + penoffset + 41.0, self.firstPenInRackPositionZ) + " ; !lift pen",
                        "G0 F{} X{:0.3f} Z{:0.3f}".format(self.speedTravelFast, self.firstPenInRackPositionX + penoffset + 41.0, self.firstPenInRackPositionZ - 152.0) + " ; !go under pen"]

        putlines[1:1] = [ "M203 Z" + str(self.maxFeedrateZFast) + " ; sets faster z max feedrate" ]
        putlines.append(  "M203 Z" + str(self.maxFeedrateZSlow) + " ; restore z max feedrate")

        return putlines

    def transfromToDrawLine(self, gcode, additionalZ = 0):
        coord = getCoord(gcode, "FXYZ")
        newgcode = gcode[:3]
        
        F = getValue(coord, "F")
        if F != None:
            newgcode += "F" + str(self.speedDraw)
            
        X = getValue(coord, "X")
        if X != None:
            newgcode += " X" + "{:0.3f}".format(X + self.penTipOffsetX)
            
        Y = getValue(coord, "Y")
        if Y != None:
            newgcode += " Y" + "{:0.3f}".format(Y + self.penTipOffsetY)
            
        Z = getValue(coord, "Z", self.currentPosZ)
        Z += additionalZ
        newgcode += " Z" + "{:0.3f}".format(Z + self.penTipOffsetZ)

        commentParts = gcode.partition(';')
        if commentParts[2] != "":
            newgcode += " ;" + commentParts[2]
        
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
            newline += " Z" + "{:0.3f}".format(self.currentPosZ)

        return "".join([newline, parts[1], parts[2]])

    def __init__(self):
        # regex pattern to identify a layer change
        self.layerChangePattern = re.compile(r'^;LAYER_CHANGE') #re.compile(r';LAYER:')
        # regex pattern to identify end of print so we can emit final draw lines
        self.printEndPattern = re.compile(r'^;END')

        # do we need to differentiate between drawn and printed objects?
        self.useObjects = True
        # names of objects that will be used for drawing only. all others will be printed regularly.
        self.objectsDrawable = [ "COLORINFO" ]
        # regex pattern to capture object changes
        self.objectStartPattern = re.compile(r'; printing object\s(.*)')
        # regex pattern to identify the end of an object block
        self.objectStopPattern = re.compile(r'; stop printing object')

        # regex pattern to identify G0 and G1 moves
        self.g01Pattern = re.compile(r'^G[01]\s')
        
        # regex pattern to capture feature type changes
        self.typeChangePattern = re.compile(r'^;TYPE:(.*)')
        # feature types that will be used for for drawing
        self.typesDrawable = ["Top solid infill", "Perimeter", "External perimeter", "Solid infill"] #["WALL-INNER", "WALL-OUTER"]
        # feature type of wipe/prime tower
        self.typePrimeTower = "PRIME-TOWER"
        
        # high speed for faster travel to the pen rack, mm/min
        self.speedTravelFast = 10800
        # slower speed to gently grab/put the pen, mm/min
        self.speedTravelSlow = 2000

        # draw speed, mm/min. set to 0 to use printing speeds
        self.speedDraw = 3600
        
        # higher max z feedrate to reach the pen rack faster, mm/sec
        self.maxFeedrateZFast = 30
        # default max z feedrate, mm/sec
        self.maxFeedrateZSlow = 12
        
        # lift distance, mm
        self.liftZ = 2.0

        # multiplier for unretraction after drawing. unretractionLength = retractionLength * unretractionMultiplier 
        self.unretractionMultiplier = 0.5


    def emitDrawLines(self):
        if next((l for l in self.drawLinesHasData if l == True), None) != None:
            verbosePrint("start drawing for layer " + str(self.currentLayer))
            self.layerLines += ["", ""]
            self.layerLines += ["; start drawing"]

            # lift pen from current position to avoid blobbing
            self.layerLines += ["G0 X{:0.3f} Y{:0.3f} Z{:0.3f}".format(self.currentPosX, self.currentPosY, self.currentPosZ + self.liftZ) + " ; lift from current position"]

            # retract
            if self.retractionLength > 0:
                self.layerLines += ["G1 F1500 E-" + str(self.retractionLength) + " ; retract before drawing"]
                
            for i in range(8):
                if self.drawLinesHasData[i] == False:
                    continue

                verbosePrint("drawing pen " + str(i + 1))
                self.layerLines.append("; drawing pen " + str(i + 1))

                self.layerLines += self.getPen(i)
                self.layerLines.append(self.lift(self.getFirstPos(self.drawLines[i]), self.liftZ) + " ; lower pen from above the first spot")
                self.layerLines += self.drawLines[i]
                self.layerLines.append(self.lift(self.drawLines[i][-1], self.liftZ) + " ; raise pen from the last spot")
                self.layerLines += self.putPen(i)
                
                '''
                # note: order of two next command blocks is flipped because they are sequential insertions
                self.drawLines[i][1:1] = [self.lift(self.getFirstPos(self.drawLines[i]), self.liftZ) + " ; lower pen from above the first spot"]
                self.drawLines[i][1:1] = self.getPen(i)
                self.drawLines[i] += [self.lift(self.drawLines[i][-1], self.liftZ) + " ; raise pen from the last spot"]
                self.drawLines[i] += self.putPen(i)

                self.layerLines += self.drawLines[i]
                '''

            if self.retractionLength > 0:
                # unretract after drawing while moving to last position to avoid blobbing
                self.layerLines += ["G1 X{:0.3f} Y{:0.3f} Z{:0.3f} E{:0.3f}".format(self.currentPosX, self.currentPosY, self.currentPosZ + self.liftZ, self.retractionLength * self.unretractionMultiplier) + " ; unretract"]
            else:
                self.layerLines += ["G1 X{:0.3f} Y{:0.3f} Z{:0.3f}".format(self.currentPosX, self.currentPosY, self.currentPosZ + self.liftZ)]

            self.layerLines += ["G0 X{:0.3f} Y{:0.3f} Z{:0.3f}".format(self.currentPosX, self.currentPosY, self.currentPosZ) + " ; return to last pos after drawing"]
            
            self.layerLines += ["; done drawing"]
            self.layerLines += ["", ""]


    def initLayerBuffers(self):
        self.layerLines = []
        self.drawLines = [None] * 8
        self.drawLinesHasData = [False] * 8
        self.drawLinesCurrentType = [None] * 8

        for i in range(8):
            self.drawLines[i] = []
            self.drawLinesCurrentType[i] = None
            
        self.primelines = ["; moved prime tower"]
            
        self.linestoskip = 0
            
        self.zhopOffset = 3.0

    def appendLayerLineIfPrintableObject(self, line):
        if self.useObjects == False or self.currentObject == None or self.isObjectDrawable == False:
            self.layerLines.append(line)

    def flushLayerBuffers(self):
        self.emitDrawLines()
        self.outputLines += self.layerLines
        
    def execute(self, inputLines):
    
        self.firstPenInRackPositionX = self.getSettingValueByKey("FirstPenXPosition")# 28.0
        self.firstPenInRackPositionZ = self.getSettingValueByKey("FirstPenZPosition")#238.0
    
        self.penTipOffsetX = self.getSettingValueByKey("PenXOffset")#36.1
        self.penTipOffsetY = self.getSettingValueByKey("PenYOffset")#45.3
        self.penTipOffsetZ = self.getSettingValueByKey("PenZOffset")#3.2

        self.retractionLength = self.getSettingValueByKey("ExtraRetraction")
        self.interlace = self.getSettingValueByKey("Interlace")

        self.currentPosX = 0
        self.currentPosY = 0
        self.currentPosZ = 0.2

        self.currentLayer = -1
        self.initLayerBuffers()
        self.currentTool = 0
        self.currentObject = None

        self.outputLines = []

        self.isTypePrimeTower = False
        self.isTypeDrawable = False
        self.isObjectDrawable = False

        linestoskip = 0

        currentLine = -1

        #allLines = [item for sublist in data for item in sublist]

        for line in inputLines:
            
            currentLine += 1

            if linestoskip > 0:
                linestoskip -= 1
                continue

            # keep track of layer count
            m = self.layerChangePattern.search(line)
            if m:
                self.flushLayerBuffers()
                self.initLayerBuffers()
                self.currentLayer += 1
                self.layerLines.append(line)
                verbosePrint("change to layer {} ({})".format(self.currentLayer, currentLine))
                continue

            m = self.printEndPattern.search(line)
            if m:
                self.flushLayerBuffers()
                self.initLayerBuffers()
                self.currentLayer = -1
                self.layerLines.append(line)
                verbosePrint("end of print ({})".format(currentLine))
                continue
            
            # keep track of current object if enabled
            if self.useObjects:
                m = self.objectStartPattern.search(line)
                if m:
                    self.currentObject = m.groups(0)[0]
                    self.layerLines.append(line)
                    self.isObjectDrawable = self.currentObject != None and next((od for od in self.objectsDrawable if od in self.currentObject), None) != None
                    verbosePrint("start object: " + self.currentObject)
                    continue

                m = self.objectStopPattern.search(line)
                if m:
                    self.currentObject = None
                    self.layerLines.append(line)
                    verbosePrint("stop object")
                    continue

            # keep track of feature type
            m = self.typeChangePattern.search(line)
            if m:
                self.currentType = m.groups(0)[0]
                if self.currentType == self.typePrimeTower:
                    self.isTypePrimeTower = True
                    self.isTypeDrawable = False
                elif next((td for td in self.typesDrawable if td == self.currentType), None) != None:
                    self.isTypeDrawable = True
                    self.isTypePrimeTower = False
                else:
                    self.isTypeDrawable = False
                    self.isTypePrimeTower = False

                verbosePrint("change type to " + self.currentType)
                self.appendLayerLineIfPrintableObject(line)
                continue
            
            # G0/G1
            # keep track of current position
            # check if the move should be dropped or used for printing or drawing
            m = self.g01Pattern.search(line)
            if m:
                coord = getCoord(line, "XYZEF")

                # remember last known position
                X = getValue(coord, "X")
                if X != None:
                    self.currentPosX = X

                Y = getValue(coord, "Y")
                if Y != None:
                    self.currentPosY = Y

                oldPosZ = self.currentPosZ

                Z = getValue(coord, "Z")
                if Z != None:
                    self.currentPosZ = Z

                # TODO: rely on existing lift-moves or detect retraction like in the original code? problem: old code used negative E but wipe moves always have negative E.
                
                # should we draw?
                    #(self.currentObject != None and "COLORINFO" in self.currentObject) and
                if (   
                    (self.useObjects == False or (self.currentObject != None and self.isObjectDrawable)) and
                    self.currentTool > 0 and
                    self.currentLayer >= 0 and
                    self.isTypeDrawable == True and
                    self.isTypePrimeTower == False and
                    ((self.currentLayer + self.currentTool) % 2 == 0 or self.interlace == False)
                ):
                    # mark buffer as written
                    if self.drawLinesHasData[self.currentTool - 1] == False:
                        self.drawLinesHasData[self.currentTool - 1] = True
                        verbosePrint("started to fill draw buffer for pen {} at layer {}".format(self.currentTool, self.currentLayer))

                    # keep track of what type is being drawn
                    if self.drawLinesCurrentType[self.currentTool - 1] != self.currentType:
                        self.drawLines[self.currentTool - 1].append("; drawing for type: " + self.currentType)
                        self.drawLines[self.currentTool - 1].append(self.transfromToDrawLine(("G0 X{:0.3f} Y{:0.3f} Z{:0.3f}".format(self.currentPosX, self.currentPosY, self.currentPosZ))) + " ; move to tracked position")
                        self.drawLinesCurrentType[self.currentTool - 1] = self.currentType

                    # try to detect lift and amplify the move
                    additionalZ = 0
                    if(oldPosZ < self.currentPosZ):
                        additionalZ = self.liftZ

                    self.drawLines[self.currentTool - 1].append(self.transfromToDrawLine(line, additionalZ))
                else:
                    self.appendLayerLineIfPrintableObject(line)

                continue

            # keep track of tool, comment out
            if re.match(r'^T[0-8]', line):
                self.currentTool = int(line[1:2])
                self.layerLines.append(";" + line)
                verbosePrint("changed tool to {}".format(self.currentTool))
                continue
                
            # comment out other lines using "T" as a parameter
            # TODO: differentiate between commands using "T" to address a tool (e.g. M109) and commands where "T" as other meaning (e.g. M205)
            if re.search(r'T[1-8](\s|$)', line):
                self.layerLines.append(";" + line)
                continue

            # just append the new line if we did not need to process it
            self.appendLayerLineIfPrintableObject(line)

        #move prime tower to layer startswith
        #primelines.append(";end prime tower")
        #if len(primelines) > 3:
        #    newlines[2:2] = primelines

        #add drawlines
        
        self.flushLayerBuffers();

        return self.outputLines

# run this if not executed via Cura
if runsStandalone == True:
    import argparse

    parser = argparse.ArgumentParser(description='Postprocess gcode file to add colors using pens.', exit_on_error=True)
    parser.add_argument('-c', '--config', help='Path to the config json file.', required=False)
    parser.add_argument('-i', '--input', help='Path to the input gcode file.', required=True)
    parser.add_argument('-o', '--output', help='Path to the output gcode file. If not set, a <input>.processed.gcode file will be used instead. Note: Output file will be overwritten if it exists.', required=False)
    parser.add_argument('--overwrite', help='Overwrites the original file if set. Ignored when output is set.', default=False, required=False, action='store_true')
    parser.add_argument('--verbose', help='Enables verbose logging.', default=False, required=False, action='store_true')
    parser.add_argument('--noop', help=argparse.SUPPRESS, default=False, required=False, action='store_true')

    args = parser.parse_args()

    configFilename = args.config
    inputFilename = args.input
    outputFilename = args.output
    overwriteFile = args.overwrite

    # check if we need to enable verbose logging
    if args.verbose:
        def verbosePrint(msg):
            print(msg)

    if(args.noop):
        print("noop")
        exit()

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
    #partStartDelimiters = [";LAYER_CHANGE", "; generated by "]
    #partEndDelimiters = [";TYPE:Custom"]
    #script.layerPartMarker = ";LAYER_CHANGE"
    #script.typeIncludedMarkers = ["Top solid infill", "Perimeter", "External perimeter", "Solid infill"]
    
    # read input gcode file
    print("Running script on " + inputFilename)
    with open(inputFilename) as file:
        lines = file.read().splitlines()

    # execute script
    lines = script.execute(lines)

    # write output gcode file
    if outputFilename == None:
        if overwriteFile:
            outputFilename = inputFilename
        else:
            outputFilename = inputFilename.partition(".gcode")[0] + ".processed.gcode"

    print("Writing processed file to " + outputFilename);
    with open(outputFilename, "w", newline='') as file:
        file.write("\n".join(lines))

    '''
    # TODO: cura compat

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

    verbosePrint("Writing processed file to " + outputFilename);
    with open(outputFilename, "w", newline='') as file:
        for i in range(0, len(layers)):
            file.write(layers[i])
    '''