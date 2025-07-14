# Helper script to create/update the list of eumItem and eumUnit,
# reading from the EUM.xml file. From the root folder, run:
# 
# python.exe ./buildUtil/eumXMLProcess.py > eumItemUnit.txt
#
# then compare eumItemUnit.txt with the ./mikecore/eum.py 
# and copy over the missing items and units.
#  
# This requires that the BuildNativeBin.bat has been run, 
# to find the EUM.xml in the right position.

import re

# Using readlines()
eumFile = open('mikecore/bin/windows/EUM.xml', 'r')
eumLines = eumFile.readlines()
eumFile.close()

recItem = re.compile('"(eumI\w+)" MzId="(\w*)"')
recUnit = re.compile('"(eumU\w+)" MzId="(\w*)"')

itemDict = {}
unitDict = {}
for line in eumLines:
    match = recItem.search(line)
    if match:
        itemDict[int(match.group(2))] = match.group(1)
    match = recUnit.search(line)
    if match:
        unitDict[int(match.group(2))] = match.group(1)

itemKeys = list(itemDict.keys())
unitKeys = list(unitDict.keys())

itemKeys.sort()
unitKeys.sort()

print("# Predefined enums of EUM item types.");
print("#");
print("# Must be updated with every new release, or if the EUM.xml is updated");
print("# Run buildUtil\eumXMLProcess.py to create the lists");
print("class eumItem(IntEnum):");
for key in itemKeys:
    print("    {} = {}".format(itemDict[key], key))

print("")
print("# Predefined enums of EUM units.")
print("#")
print("# Must be updated with every new release, or if the EUM.xml is updated")
print("class eumUnit(IntEnum):")
for key in unitKeys:
    print("    {} = {}".format(unitDict[key], key))
        