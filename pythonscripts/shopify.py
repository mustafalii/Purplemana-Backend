import os
import gspread

scopes = ["https://spreadsheets.google.com/feeds",
          "https://www.googleapis.com/auth/spreadsheets",
          "https://www.googleapis.com/auth/drive.file",
          "https://www.googleapis.com/auth/drive",
          "https://www.googleapis.com/auth/drive.appdata"
          ]

currDir = os.getcwd()
parDir = os.path.dirname(currDir)
secretPath = os.path.join(parDir, "server", "drive_secret.json")


def addToCsv(rec):
    gc = gspread.service_account(filename=secretPath)
    wks = gc.open("ShopifyCSV").sheet1
    wks.append_row(rec, table_range="A:AU")
    print("Added record")


if __name__ == '__main__':
    record = ["customHandle", "customTitle", "customBody", "Wizards of the Coast",
              "Collectible Cards", "customTags", "", "Title", "Default Title", "", "", "", "",
              "customSKU", "28", "shopify", "1", "deny", "manual", "customPrice", "customCompare",
              "TRUE", "FALSE", "", "Imgsrc", "1", "", "FALSE", "", "", "", "",
              "", "", "", "", "", "", "", "", "", "", "", "", "oz", "", "Cost"]

    shopifyFilePath = os.path.join(parDir, "server", "public", "shopifyProduct.txt")
    file = open(shopifyFilePath)
    row = file.readlines()
    record[0], record[1], record[2], record[5], record[13], record[19], record[20], record[24], record[46] = row
    record[0] = record[0].lower().replace(" ", "-")

    for index, _ in enumerate(record):
        record[index] = record[index].strip()
        record[index] = record[index].replace("$", "").replace(",", "")
        record[index] = record[index].strip()
        if record[index].replace('.', '', 1).isdigit():
            record[index] = float(record[index])
        elif record[index] == "FALSE":
            record[index] = False
        elif record[index] == "TRUE":
            record[index] = True
    addToCsv(record)
