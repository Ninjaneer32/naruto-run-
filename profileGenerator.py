import csv # needed to read csv files
import yaml # needed to write config files

with open('./vendorLists/oui.csv', mode='r', encoding='utf8') as infile: # large registry
    reader = csv.reader(infile)

    largeDict = {rows[1]:rows[2] for rows in reader}


with open('./vendorLists/mam.csv', mode='r', encoding='utf8') as infile: # medium registry
    reader = csv.reader(infile)

    midDict = {rows[1]:rows[2] for rows in reader}


with open('./vendorLists/oui36.csv', mode='r', encoding='utf8') as infile: # small registry
    reader = csv.reader(infile)

    smallDict = {rows[1]:rows[2] for rows in reader}

print("Naruto decoy config generator:")

while True:
    searchTerm = input("Enter the vendor or name to look for: ").lower()

    print(f"Searching for: {str(searchTerm)}")

    # list of valid vendors
    results = []
    macList = []

    # test large registry
    print("Searching MAC Address Block Large (MA-L / OUI)")

    for i in largeDict.keys():

        if (str(largeDict[i]).lower().find(searchTerm) != -1): # make string lower case to remove case sensitivity
            results.append([i, largeDict[i]])
            macList.append(i)

    # test medium registry
    print("Searching MAC Address Block Medium (MA-M / MAM)")

    for i in midDict.keys():
        if (str(midDict[i]).lower().find(searchTerm) != -1): # make string lower case to remove case sensitivity
            results.append([i, midDict[i]])
            macList.append(i)

    # test small registry
    print("Searching MAC Address Block Small (MA-S / OUI36)")

    for i in smallDict.keys():
        if (str(smallDict[i]).lower().find(searchTerm) != -1): # make string lower case to remove case sensitivity
            results.append([i, smallDict[i]])
            macList.append(i)

    # prints out matches
    print(f"Found {str(len(results))} matches")

    for i in range(len(results)):
        print(f"{str(results[i][1])} : {str(results[i][0])}")
    
    confirm = input("Type yes or y to use these MAC Blocks, or anything else to restart : ").lower()

    if confirm.startswith('y'): # if use confirms continue making the config
        
        ssidStartString = input("Enter whatever static string you want the decoy SSIDs to start with: ")

        fillerType = int(input("Enter 1 for the filler values to be numbers, or 2 for it to be hex: "))

        fillerLength = int(input("Enter the number of characters the filler part of the SSID should be: "))

        fileName = input("Enter the file name for the profile:")

        if fillerType == 1: 
            filler = 'num'
        else:
            filler = 'hex'

        # bundles everything together into yaml data
        data = {
            "startString" : ssidStartString,
            "fillerType" : filler, 
            "fillerLength" : fillerLength, 
            "macs" : macList
        }

        with open(f'./cloneConfigs/{fileName}.yml', 'w') as outFile:
            yaml.dump(data, outFile, default_flow_style=False, sort_keys=False)

        print(f"Wrote data to {fileName}.yml\n\n")