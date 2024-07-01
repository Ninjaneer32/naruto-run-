# quick program to download MAC vendor lists from the IEE

import requests # needed to make web requests

# The URL to the MA-L CSV - the Large Block Registry
malURL = "http://standards-oui.ieee.org/oui/oui.csv"

# this is the URL to the MA-M CSV - the Medium Block Registry
mamURL = "http://standards-oui.ieee.org/oui28/mam.csv"

# this is the URL to the MA-S CSV - the Small Bloc Registry
masURL = "http://standards-oui.ieee.org/oui36/oui36.csv"

# Download MAM 
response = requests.get(mamURL)
file_Path = './vendorLists/mam.csv'
 
if response.status_code == 200:
    with open(file_Path, 'wb') as file:
        file.write(response.content)
    print('MAM downloaded successfully')
else:
    print('Failed to download MAM')

# Download OUI
response = requests.get(malURL)
file_Path = './vendorLists/oui.csv'
 
if response.status_code == 200:
    with open(file_Path, 'wb') as file:
        file.write(response.content)
    print('OUI downloaded successfully')
else:
    print('Failed to download OUI')

# Download OUI36 
response = requests.get(masURL)
file_Path = './vendorLists/oui36.csv'
 
if response.status_code == 200:
    with open(file_Path, 'wb') as file:
        file.write(response.content)
    print('OUI36 downloaded successfully')
else:
    print('Failed to download OUI36')