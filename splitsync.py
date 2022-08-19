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
import datetime;

# constants

FILE_PREFIX = "Super Metroid Practice - "
FILE_REGEX = re.compile("- (\\d{2}) -")
BLANK_FILE_XML = "<?xml version=\"1.0\" encoding=\"UTF-8\"?> <Run version=\"1.7.0\"> <GameIcon></GameIcon> <GameName>Super Metroid</GameName> <CategoryName>Any%</CategoryName> <Metadata> <Run id=\"\" /> <Platform usesEmulator=\"True\">Super Nintendo</Platform> <Region> </Region> <Variables> <Variable name=\"Route\">KPDR</Variable> <Variable name=\"Region\">NTSC</Variable> </Variables> </Metadata> <Offset>00:00:00</Offset> <AttemptCount>0</AttemptCount> <AttemptHistory> </AttemptHistory> <Segments> </Segments> <AutoSplitterSettings /> </Run>"
BLANK_SEGMENT_XML = "<Segment><Name /><Icon /><SplitTimes /><BestSegmentTime /><SegmentHistory /></Segment>"


# inputs

fullRunPath = "Test Data\\Super Metroid - Any% KPDR.lss"
segmentsPath = "Test Data\\KPDR Segment Practice Splits v2_1"


# functions

def validateFullRunPath():
    path = Path(fullRunPath)
    if not path.is_file():
        print("File was not found: " + fullRunPath)
        exit()
    return

def validateSegmentsPath():
    path = Path(segmentsPath)
    if not path.is_dir():
        print("Directory for segment splits was not found: " + segmentsPath)
        exit()
    return

def getSortedKeys(filesDict):
    return sorted(filesDict, key=lambda key: filesDict[key])
    
def getAllSplitFiles():
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
    print("Please select your full run file. Press any key to continue...")
    click.getchar()
    Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
    filename = askopenfilename(initialdir=os.getcwd()) # show an "Open" dialog box and return the path to the selected file
    if filename == "":
        print("No file selected for full run. Aborting...")
        exit()
    print(filename)
    return filename

def dirSelect():
    Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
    folderName = filedialog.askdirectory(initialdir=os.getcwd()) # show an "Open" dialog box and return the path to the selected file
    return folderName

def generateOutputFolder():
    path = Path("Output")
    if not path.is_dir():
        os.mkdir("Output")
    
    ct = os.path.join("Output", datetime.datetime.now().strftime("%Y-%m-%d %H.%M.%S"))
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

def createBlankSegmentWithName(runSegments, Name):
    newSegment = ET.fromstring(BLANK_SEGMENT_XML)
    newSegment.findall("Name")[0].text = Name
    runSegments.append(newSegment)
    return

def generateCeresSegment(runSegments):
    createBlankSegmentWithName(runSegments, "-Ceres Ridley")
    createBlankSegmentWithName(runSegments, "-Ridley Escape")
    createBlankSegmentWithName(runSegments, "-Ceres Escape")
    createBlankSegmentWithName(runSegments, "{00 - Ceres Escape}Landing Site")
    return

def generateRunFile(segmentFiles):
    tree = ET.parse("Test Data\\Super Metroid blank.lss")
    runXML = ET.fromstring(BLANK_FILE_XML)
    runSegments = runXML.findall("Segments")[0]

    generateCeresSegment(runSegments)

    # for loop to add each segment's splits
    for i in range(len(segmentFiles)):
        segmentPath = os.path.join(segmentsPath, segmentFiles[i + 1])
        tree = ET.parse(segmentPath)
        segmentXml = tree.getroot()

        segments = segmentXml.findall("Segments")[0]
        for j in range(len(segments)):
            # if this is a duplicate of previous segment, ignore it
            print("Previous Segment: " + runSegments[-1].findall("Name")[0].text)
            print("Current Segment: " + segments[j].findall("Name")[0].text)
            if "}" in runSegments[-1].findall("Name")[0].text:
                print("Cut header: " + runSegments[-1].findall("Name")[0].text.split("}")[1])
                if segments[j].findall("Name")[0].text == runSegments[-1].findall("Name")[0].text.split("}")[1]:
                    continue

            newSegment = ET.fromstring("<Segment />")
            for segNode in segments[j]:
                if segNode.tag == "SplitTimes":
                    newSplitTimes = ET.SubElement(newSegment, "SplitTimes")
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
                newSegment.append(segNode)
            runSegments.append(newSegment)

    # pretty up the xml
    ET.indent(runXML)

    # generate file(s)
    outputFolder = generateOutputFolder()
    outputFilePath = os.path.join(outputFolder, "Super Metroid Full Segments.lss")
    with open(outputFilePath, "w") as f:
        f.write(ET.tostring(runXML, encoding="unicode", method="xml"))

    return

def generateRun():
    print("Please select a directory containing segment files. Press any key to continue...")
    click.getchar()
    folderName = dirSelect()
    if folderName == "":
        print("No folder selected for segment files. Aborting...")
        exit()
    print(folderName)

    validateSegmentsPath()
    segmentFiles = getAllSplitFiles()
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

    print("Merging into a single run file...")
    generateRunFile(segmentFiles)
    return

def displayMenu():
    print("Which action to perform?\n1. Output Segment Times for Spreadsheet\n2. Sync Gold Splits\n3. Generate run file from segment files\n4. Add run PB comparison to segment files\ne. Exit\n")
    menuInput = click.getchar()
    if menuInput == "1":
        print("not implemented")
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
