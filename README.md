# splitSync
Read LiveSplit splits, merge data between full runs and segments.  This is intended to be used with Super Metroid using segment data from Kuru.

# Installation
1. Download splitsync.py from this repo
2. Install Python3 https://www.python.org/downloads/
3. In a command line / terminal, make sure you have pip configured (you may need to run as administrator)
    - Type "pip" in the console and see if it is registered
    - If it's not, edit your PATH environment variable to include the exe location
        - Review this guide for that: https://www.activestate.com/resources/quick-reads/how-to-install-pip-on-windows/
4. Install any dependencies that are missing
    - Likely not installed is "click", using this as the example:
        - in the console, type: "pip install click"
    - Repeat for any other missing dependencies, which can be viewed at the top of the script file as imports

# Usage
1. Run the script as **"python splitsync.py"**
2. You will be prompted with a menu, press a key corresponding with which action you want to take
3. Press 'e' to exit when done if the script is back at the menu, some actions will halt the script automatically
4. Resulting output files will be stored in an **"Output"** folder at the same directory location as where the script was run from.
    - Results are split into sub folders based on current timestamp as to not lose original files or overwrite anything

# Assumptions
There are many assumptions that exist depending on the action.

## Global assumptions
1. **Naming Patterns** - When being asked to provide segment split files, you will be prompted for a folder location that holds the segments.  The script will only identify files that have this naming pattern:
    - **"Super Metroid Practice - ##"** as the prefix, followed by anything else
    - All other files in the directory will be ignored
2. **Digit Identifiers** - Segment file names include 2 digits as previously mentioned.  These are super important and are used for ordering of segments.
3. **LiveSplit Settings** - The following settings are defaulted to these values, you may need to tweak manaully if you care about them:
    - GameName = "Super Metroid"
    - CategoryName = "Any%"
    - Platform usesEmulator = "True"
    - Route = KPDR
    - Region = NTSC

## Generating a full run file from segment splits
1. **Sequential File Numbering** - When specifying the segment split file folder, there is an assumption that you present all the required segments.  The script will check that you have a segment "01", and that there are sequential segment files proceeding that one.  If you have duplicates or missing numbers, the script will let you know and abort.
2. **Expected Starting Segment** - Currently we assume that Ceres is not included and that the first split begins at the ship in landing site.  The script will automatically fill in splits for Ceres without a corresponding segment for it.
3. **Duplicate splits** - If sequential segments have the same split (ie, the last split of segment 1 is the first split of segment 2), the script will automatically remove the latter split.
    - NOTE: this only works if the splits have identical names