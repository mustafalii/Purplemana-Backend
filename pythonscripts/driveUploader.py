from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
import gspread
from datetime import date
import os

# Get Parent Directory for platform independent path browsing
currDir = os.getcwd()
parDir = os.path.dirname(currDir)


# Connect to Inventory spreadsheet and add a record
def updateInventory(fileInfo):
    filePath = os.path.join(parDir, "server", "drive_secret.json")
    gc = gspread.service_account(filename=filePath)
    inv = gc.open("MainInventory").sheet1
    inv.append_row(fileInfo)


# Add image to specific folder in google drive
def uploadImage(imageName, imagePath):
    scopes = ["https://spreadsheets.google.com/feeds",
              "https://www.googleapis.com/auth/spreadsheets",
              "https://www.googleapis.com/auth/drive.file",
              "https://www.googleapis.com/auth/drive",
              "https://www.googleapis.com/auth/drive.appdata"
              ]

    filePath = os.path.join(parDir, "server", "drive_secret.json")
    credentials = ServiceAccountCredentials.from_json_keyfile_name(filePath, scopes)
    service = build('drive', 'v3', credentials=credentials)
    resultsDict = service.files().list(fields="nextPageToken, files(id, name)").execute()

    myFiles = resultsDict.get('files', [])

    # Get ID of Scanned folder to serve as parentFolderId
    for file in myFiles:
        if file['name'] == 'Scanned':
            scannedFolderId = file['id']

            # body of image to be uploaded
            fileBody = {
                'name': imageName,
                'parents': [scannedFolderId]
            }
            media = MediaFileUpload(imagePath, mimetype='image/png', resumable=True)
            service.files().create(body=fileBody, media_body=media).execute()
            print("Image uploaded to scanned folder.")
            break

    # imageFileName = s/tr(date) + "_" + source + "_" + cardName + "_" + grade + "_" + slot


if __name__ == "__main__":
    filePath = os.path.join(parDir, "server", "public", "updateInventory.txt")
    file = open(filePath)
    imagesLineList = file.readlines()
    for line in imagesLineList:
        lineArray = line.split(",")
        lineArray[1] = lineArray[1].replace("\n", "")
        uploadImage(lineArray[0], lineArray[1])
        newRecord = lineArray[0].split("_")
        record = ["In Hand", newRecord[2], newRecord[0], newRecord[1], newRecord[3], str(date.today())]
        updateInventory(record)
        print(lineArray)
