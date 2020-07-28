import gspread
import os

# Get paths for platform independent path browsing
currDir = os.getcwd()
parDir = os.path.dirname(currDir)
secretPath = os.path.join(parDir, "server", "drive_secret.json")


# Fetch inventory from Google sheets
def getInventory():
    gc = gspread.service_account(filename=secretPath)
    inv = gc.open("MainInventory").sheet1
    recs = inv.get_all_values()
    return recs


# Write the output to inventory.txt
def writeInventory(recs):
    invPath = os.path.join(parDir, "server", "public", "inventory.txt")
    with open(invPath, 'w') as writer:
        for record in recs:
            for i in range(len(record)):
                if i == len(record) - 1:
                    writer.write(record[i] + "\n")
                else:
                    writer.write(record[i] + "\t")


if __name__ == "__main__":
    records = getInventory()
    writeInventory(records)
