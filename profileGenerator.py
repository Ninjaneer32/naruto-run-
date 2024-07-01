import csv # needed to read csv files

with open('./vendorLists/oui.csv', mode='r', encoding='utf8') as infile: # large registry
    reader = csv.reader(infile)

    largeDict = {rows[1]:rows[2] for rows in reader}


with open('./vendorLists/mam.csv', mode='r', encoding='utf8') as infile: # medium registry
    reader = csv.reader(infile)

    midDict = {rows[1]:rows[2] for rows in reader}


with open('./vendorLists/oui36.csv', mode='r', encoding='utf8') as infile: # small registry
    reader = csv.reader(infile)

    smallDict = {rows[1]:rows[2] for rows in reader}


searchTerm = input("Enter the vendor or name to look for: ").lower()

print(f"Searching for: {str(searchTerm)}")

# list of valid vendors
results = []

# test large registry
print("Searching MAC Address Block Large (MA-L / OUI)")

for i in largeDict.keys():

    if (str(largeDict[i]).lower().find(searchTerm) != -1): # make string lower case to remove case sensitivity
        results.append([i, largeDict[i]])

# test medium registry
print("Searching MAC Address Block Medium (MA-M / MAM)")

for i in midDict.keys():
    if (str(midDict[i]).lower().find(searchTerm) != -1): # make string lower case to remove case sensitivity
        results.append([i, midDict[i]])

# test small registry
print("Searching MAC Address Block Small (MA-S / OUI36)")

for i in smallDict.keys():
    if (str(smallDict[i]).lower().find(searchTerm) != -1): # make string lower case to remove case sensitivity
        results.append([i, smallDict[i]])


print(f"Matches found: \n{str(results)}")