# Runs on Python3

import xml.etree.ElementTree as ET
from pathlib import Path
from os import listdir
from os.path import isfile, join
import os
import re
import click
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from tkinter import filedialog
import datetime
from datetime import *
import pyperclip

# constants

FILE_PREFIX = "Super Metroid Practice - "
FILE_REGEX = re.compile("- (\\d{2}) -")
BLANK_FILE_XML = "<?xml version=\"1.0\" encoding=\"UTF-8\"?> <Run version=\"1.7.0\"> <GameIcon></GameIcon> <GameName>Super Metroid</GameName> <CategoryName>Any%</CategoryName> <Metadata> <Run id=\"\" /> <Platform usesEmulator=\"True\">Super Nintendo</Platform> <Region> </Region> <Variables> <Variable name=\"Route\">KPDR</Variable> <Variable name=\"Region\">NTSC</Variable> </Variables> </Metadata> <Offset>00:00:00</Offset> <AttemptCount>0</AttemptCount> <AttemptHistory> </AttemptHistory> <Segments> </Segments> <AutoSplitterSettings /> </Run>"
BLANK_SEGMENT_XML = "<Segment><Name /><Icon /><SplitTimes><SplitTime><RealTime /></SplitTime></SplitTimes><BestSegmentTime><RealTime /></BestSegmentTime><SegmentHistory /></Segment>"
INIT_PAD_AMOUNT = "00:02:15.0000000"
SEGMENT_PB = "Spliced PB"

# fields

padAmount = INIT_PAD_AMOUNT
adjustments = {
    "Charge Beam Missile": {"diff": "00:00:16.0000000", "isAdd": True, "isUsed": False},
    "Leaving HJB": {"diff": "00:00:14.0000000", "isAdd": True, "isUsed": False},
    "West Ocean": {"diff": "00:00:21.0000000", "isAdd": True, "isUsed": False},
    "Botwoon's Room": {"diff": "00:00:05.0000000", "isAdd": False, "isUsed": False},
    "The Worst Room in the Game": {"diff": "00:00:10.0000000", "isAdd": True, "isUsed": False},
    "Metroid Room 2": {"diff": "00:01:10.0000000", "isAdd": True, "isUsed": False}
}

# functions

def validateFilePath(fullRunPath):
    path = Path(fullRunPath)
    if not path.is_file():
        print("File was not found: " + fullRunPath)
        exit()
    return

def validateSegmentsPath(segmentsPath):
    path = Path(segmentsPath)
    if not path.is_dir():
        print("Directory for segment splits was not found: " + segmentsPath)
        exit()
    return

def getSortedKeys(filesDict):
    return sorted(filesDict, key=lambda key: filesDict[key])
    
def getAllSplitFiles(segmentsPath):
    segmentFiles = [f for f in listdir(segmentsPath) if isfile(join(segmentsPath, f)) and f.startswith(FILE_PREFIX)]
    filesDict = {}
    for f in segmentFiles:
        result = FILE_REGEX.search(f)
        if result == None: continue
        segmentNum = result.group(1)
        if segmentNum == None:
            print("Found file without a segment number: " + f)
            continue
        filesDict[int(segmentNum)] = f

    return filesDict

def fileSelect():
    Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
    filename = askopenfilename(initialdir=os.getcwd()) # show an "Open" dialog box and return the path to the selected file
    return filename

def dirSelect():
    Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
    folderName = filedialog.askdirectory(initialdir=os.getcwd()) # show an "Open" dialog box and return the path to the selected folder
    return folderName

def generateOutputFolder():
    path = Path("Output")
    if not path.is_dir():
        os.mkdir("Output")
    
    ct = os.path.join("Output", datetime.now().strftime("%Y-%m-%d %H.%M.%S"))
    os.mkdir(ct)

    return ct

def hasSequentialSegments(sortedKeys):
    i = 1
    for key in sortedKeys:
        if key != i:
            print("The segments folder does not contain sequential splits, are some missing?")
            print("Missing segment #" + str(i))
            print("Unable to continue merging into a run file. Aborting...")
            exit()
        i = i + 1
    return

def createBlankSegmentWithName(runSegments, name, split, best):
    newSegment = ET.fromstring(BLANK_SEGMENT_XML)
    newSegment.findall("Name")[0].text = name
    newSegment.findall("SplitTimes")[0][0].attrib["name"] = SEGMENT_PB
    newSegment.findall("SplitTimes")[0][0].findall("RealTime")[0].text = split
    newSegment.findall("BestSegmentTime")[0].findall("RealTime")[0].text = best
    runSegments.append(newSegment)
    return

def generateCeresSegment(runSegments):
    createBlankSegmentWithName(runSegments, "-Ceres Ridley", "00:00:30.0000000", "00:00:30.0000000")
    createBlankSegmentWithName(runSegments, "-Ridley Escape", "00:01:00.0000000", "00:00:30.0000000")
    createBlankSegmentWithName(runSegments, "-Ceres Escape", "00:01:30.0000000", "00:00:30.0000000")
    createBlankSegmentWithName(runSegments, "{00 - Ceres Escape}Landing Site", "00:02:01.0000000", "00:00:31.0000000")
    return

def padSplitTime(split, adjustment, isAdd = True, updatePadTime = False):
    global padAmount
    origTime = split.text.split(".")
    dtSplit = datetime.strptime(origTime[0], "%H:%M:%S")
    padSplit = datetime.strptime(adjustment.split(".")[0], "%H:%M:%S")
    if isAdd:
        dtSplit = dtSplit + timedelta(seconds = padSplit.second)
        dtSplit = dtSplit + timedelta(minutes = padSplit.minute)
        dtSplit = dtSplit + timedelta(hours = padSplit.hour)
    else:
        dtSplit = dtSplit - timedelta(seconds = padSplit.second)
        dtSplit = dtSplit - timedelta(minutes = padSplit.minute)
        dtSplit = dtSplit - timedelta(hours = padSplit.hour)
    split.text = dtSplit.strftime("%H:%M:%S") + "." + origTime[1]

    if updatePadTime:
        print("Updated padTime: " + split.text)
        padAmount = split.text
    return

def adjustSplitTime(segmentName, split, isSplit):
    if segmentName in adjustments.keys():
        adjustment = adjustments[segmentName]
        padSplitTime(split, adjustment["diff"], adjustment["isAdd"], isSplit)
        adjustment["isUsed"] = True
    return

def validateAllAdjustments():
    for key in adjustments:
        if adjustments[key]["isUsed"] == False:
            print("Failed to find split name to adjust: " + key)
            print("Aborting...")
            exit()
    return

def generateRunFile(segmentsPath, segmentFiles):
    global padAmount

    runXML = ET.fromstring(BLANK_FILE_XML)
    runSegments = runXML.findall("Segments")[0]

    generateCeresSegment(runSegments)

    # add each segment's splits
    for i in range(len(segmentFiles)):
        segmentPath = os.path.join(segmentsPath, segmentFiles[i + 1])
        tree = ET.parse(segmentPath)
        segmentXml = tree.getroot()

        segments = segmentXml.findall("Segments")[0]
        for j in range(len(segments)):
            # if this is a duplicate of previous segment, ignore it
            if "}" in runSegments[-1].findall("Name")[0].text:
                if segments[j].findall("Name")[0].text == runSegments[-1].findall("Name")[0].text.split("}")[1]:
                    continue

            newSegment = ET.fromstring("<Segment />")
            segName = segments[j].findall("Name")[0].text
            for segNode in segments[j]:
                if segNode.tag == "SplitTimes":
                    for time in segNode[0].findall("GameTime"):
                        segNode[0].remove(time)
                    
                    newSplitTimes = ET.SubElement(newSegment, "SplitTimes")
                    segNode[0].attrib["name"] = SEGMENT_PB

                    timeNode = segNode[0].findall("RealTime")[0]
                    padSplitTime(timeNode, padAmount, True, False)
                    adjustSplitTime(segName, timeNode, True)

                    if j == len(segments) - 1:
                        padAmount = timeNode.text
                    newSplitTimes.append(segNode[0])
                    continue
                if segNode.tag == "SegmentHistory":
                    ET.SubElement(newSegment, "SegmentHistory")
                    continue
                if segNode.tag == "Name":
                    name = ET.SubElement(newSegment, "Name")
                    if j == (len(segments) - 1):
                        category = segmentXml.findall("CategoryName")[0].text
                        name.text = "{" + category + "}" + segNode.text
                    else:
                        name.text = "-" + segNode.text
                    continue
                if segNode.tag == "BestSegmentTime":
                    for time in segNode.findall("GameTime"):
                        segNode.remove(time)
                    
                    # Special case from adding Ceres
                    if segName == "Morph Ball":
                        padSplitTime(segNode[0], "00:00:14.0000000", True, False)
                    else:
                        adjustSplitTime(segName, segNode[0], False)

                    newSegment.append(segNode)
                    continue
                newSegment.append(segNode)
            runSegments.append(newSegment)

    validateAllAdjustments()

    # pretty up the xml
    ET.indent(runXML)

    # generate file(s)
    outputFolder = generateOutputFolder()
    outputFilePath = os.path.join(outputFolder, "Super Metroid Full Segments.lss")
    with open(outputFilePath, "w") as f:
        f.write(ET.tostring(runXML, encoding="unicode", method="xml"))

    return

def getSegmentsDir():
    print("Please select a directory containing segment files. Press any key to continue...")
    click.getchar()
    segmentsPath = dirSelect()
    if segmentsPath == "":
        print("No folder selected for segment files. Aborting...")
        exit()
    print(segmentsPath)
    validateSegmentsPath(segmentsPath)

    segmentFiles = getAllSplitFiles(segmentsPath)
    sortedKeys = getSortedKeys(segmentFiles)

    print("Found segment files (sorted):")
    for key in sortedKeys:
        print(segmentFiles[key])

    print("Does this look correct? Press y to continue or n to abort.\n")
    _continue = click.getchar()
    if _continue != 'y':
        print("Aborting...")
        exit()

    hasSequentialSegments(sortedKeys)
    return segmentsPath, segmentFiles

def generateRun():
    segmentsPath, segmentFiles = getSegmentsDir()
    
    print("Merging into a single run file...")
    generateRunFile(segmentsPath, segmentFiles)
    return

def outputSegmentTimes():
    segmentsPath, segmentFiles = getSegmentsDir()

    # for loop to add each segment's splits
    outputStr = ""
    for i in range(len(segmentFiles)):
        segmentPath = os.path.join(segmentsPath, segmentFiles[i + 1])
        tree = ET.parse(segmentPath)
        segmentXml = tree.getroot()
        segments = segmentXml.findall("Segments")[0]
        for segment in segments:
            splitTime = segment.findall("SplitTimes")[0][0].findall("RealTime")[0].text
            splitTime = splitTime.replace("00:", "")
            splitTime = splitTime.lstrip("0")
            dotIndex = splitTime.index(".")
            splitTime = splitTime[:dotIndex + 3]
            outputStr = outputStr + splitTime + "\n"
        outputStr = outputStr + "\n"
    
    pyperclip.copy(outputStr)
    print("Segment Times have been copied to your clipboard")
    return

def displayMenu():
    print("")
    print("Which action to perform?\n1. Output Segment Times for Spreadsheet\n2. Sync Gold Splits\n3. Generate run file from segment files\n4. Add run PB comparison to segment files\ne. Exit\n")
    menuInput = click.getchar()
    if menuInput == "1":
        outputSegmentTimes()
        return
    if menuInput == "2":
        print("not implemented")
        return
    if menuInput == "3":
        generateRun()
        return
    if menuInput == "4":
        print("not implemented")
        return
    if menuInput == "e":
        exit()
    
    print("Unknown answer, please try again: " + menuInput)
    return

# start

while True:
    displayMenu()
