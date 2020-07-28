# VIRTUAL ENV INSTRUCTIONS: https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/
import numpy as np
import cv2
import preprocess as pp
from transform import four_point_transform
import os
import TrainAndTest as slotDetector


# Resize Image
def resize_image(image):
    min_side = image.shape[0]
    max_size = 1000
    scale_f = max_size / min_side
    resized_img = cv2.resize(
        image,
        (int(image.shape[1] * scale_f), int(image.shape[0] * scale_f)),
        interpolation=cv2.INTER_AREA,
    )
    return resized_img


# Split image into bottom half and top half
def splitHalf(image):
    startTopH = 50
    half_h = 500
    startBottomH = 550
    top_half = image[startTopH:half_h]
    bottom_half = image[startBottomH:]
    return top_half, bottom_half


# Compute Epsilon for padding final crop
def computeEps(w, h):
    area = w * h
    if area <= 150000:
        return 20


# Detect cards through pre-processing and finding contours
def detectCards(image):
    toWarp = image.copy()
    cropped_dict = dict()
    # cropped_list = {}
    adjusted = pp.histogram_adjust(image.copy())
    segmented = pp.segmentation(adjusted)
    contours, hierarchy = cv2.findContours(
        np.uint8(segmented), cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE
    )
    contours_sorted = sorted(contours, key=cv2.contourArea, reverse=True)
    hull_list = []
    for cnt in contours_sorted[:10]:
        hull = cv2.convexHull(cnt)
        x, y, w, h = cv2.boundingRect(hull)
        if pp.isCardRect(x, y, w, h, hull_list):
            hull_list.append(hull)
            img_box = cv2.rectangle(
                image, (x, y), (x + w, y + h), color=(0, 255, 0), thickness=4
            )
            eps = computeEps(w, h)
            rect_point = np.array(
                [
                    [x - eps, y - eps],
                    [x + w + eps, y - eps],
                    [x + w + eps, y + h + eps],
                    [x - eps, y + h + eps],
                ]
            )
            warped = four_point_transform(toWarp, rect_point)
            # cropped_list.append(warped)
            cropped_dict[x - eps] = warped
    return cropped_dict, image


# Auto-cropping class
class Autocropper:
    def __init__(self, image):
        self.original_image = image
        # pp.show_image(image)
        self.resized_image = resize_image(image)
        self.topHalf, self.bottomHalf = splitHalf(self.resized_image)
        self.detected = []
        self.cropped = []

        cropped, detected = detectCards(self.topHalf)
        for i in sorted(cropped.keys()):
            cropped[i] = cv2.cvtColor(
                cropped[i], cv2.COLOR_BGR2RGB
            )
            self.cropped.append(cropped[i])
        detected = cv2.cvtColor(detected, cv2.COLOR_BGR2RGB)
        self.detected.append(detected)

        cropped, detected = detectCards(self.bottomHalf)
        for i in sorted(cropped.keys()):
            cropped[i] = cv2.cvtColor(
                cropped[i], cv2.COLOR_BGR2RGB
            )
            self.cropped.append(cropped[i])
        detected = cv2.cvtColor(detected, cv2.COLOR_BGR2RGB)
        self.detected.append(detected)


# Combine the back-side and front-side of each crop
def combineCrops(front, back):
    stacked = []
    for i in range(len(front)):
        cropFront = front[i]
        cropBack = back[i]
        max_height = max(cropFront.shape[0], cropBack.shape[0])
        max_width = max(cropFront.shape[1], cropBack.shape[1])
        final_image_front = np.zeros((max_height, max_width, 3), dtype=np.uint8)
        final_image_back = np.zeros((max_height, max_width, 3), dtype=np.uint8)
        final_image_front[:cropFront.shape[0], :cropFront.shape[1]] = cropFront
        final_image_back[:cropBack.shape[0], :cropBack.shape[1]] = cropBack
        stack = np.hstack((final_image_front, final_image_back))
        stacked.append(stack)
    return stacked


# Area for slot letter
def getLetterArea(image):
    image = image[0:50, 30:80]
    return image


if __name__ == "__main__":
    # Get Parent Directory
    currDir = os.getcwd()
    parDir = os.path.dirname(currDir)
    scannedCardsPath = os.path.join(parDir, "server", "public", "images", "scannedCards")
    croppedCardsPath = os.path.join(parDir, "server", "public", "images", "croppedCards")
    # path = "../server/public/images/scannedCards"
    imagesList = os.listdir(scannedCardsPath)
    cropList = []
    for im in imagesList:
        imagePath = os.path.join(scannedCardsPath, im)
        img = cv2.imread(imagePath)
        print("Running Autocrop on Scanned Image...")
        autoCrop = Autocropper(img)  # autoCrop.detected stored [topHalfDetected, bottomHalfDetected]
        cropList.append(autoCrop.cropped)  # autoCrop.cropped stores [FrontScanCrops, BackScanCrops]
        print("Writing detected cards to disk...")
        topName = "topHalf_" + im
        bottomName = "bottomHalf_" + im
        topDetectedPath = os.path.join(parDir, "server", "public", "images", "detectedCards", topName)
        bottomDetectedPath = os.path.join(parDir, "server", "public", "images", "detectedCards", bottomName)
        cv2.imwrite(topDetectedPath, cv2.cvtColor(autoCrop.detected[0], cv2.COLOR_RGB2BGR))
        cv2.imwrite(bottomDetectedPath, cv2.cvtColor(autoCrop.detected[1], cv2.COLOR_RGB2BGR))

    print("Writing cropped-joined cards to disk...")
    count = 0
    for card in combineCrops(cropList[0], cropList[1]):
        cropName = "crop" + str(count) + ".png"
        cardPath = os.path.join(croppedCardsPath, cropName)
        cv2.imwrite(cardPath, cv2.cvtColor(card, cv2.COLOR_RGB2BGR))
        count += 1

    path = os.path.join(scannedCardsPath, imagesList[0])
    img = cv2.imread(path)
    img = resize_image(img)
    img = getLetterArea(img)
    cv2.imwrite("slotPicture.png", img)
    slotDetector.detect()
    print("Done")
