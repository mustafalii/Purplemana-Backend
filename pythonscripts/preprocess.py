import cv2
import matplotlib.pyplot as plt


# Display Image
def show_image(some_image):
    plt.imshow(cv2.cvtColor(some_image, cv2.COLOR_BGR2RGB))
    plt.show()


# Histogram adjust the image
def histogram_adjust(some_image, cliplimit=3, tileGridSize=(4, 4), crop=False):
    clahe = cv2.createCLAHE(clipLimit=cliplimit, tileGridSize=tileGridSize)
    lab = cv2.cvtColor(some_image, cv2.COLOR_BGR2LAB)
    lightness, a, b = cv2.split(lab)
    corrected_lightness = clahe.apply(lightness)
    l_img = cv2.merge((corrected_lightness, a, b))
    adjusted = cv2.cvtColor(l_img, cv2.COLOR_LAB2BGR)
    return adjusted


# Apply adaptive threshold
def adaptive_threshold(some_img):
    """
    Adaptive Thresholding
    """
    denom = 100
    # print("Adaptive Thresholding Image...")
    max_side = max(some_img.shape[0], some_img.shape[1])
    block_size = 2 * (max_side // denom) + 1
    thresh = cv2.adaptiveThreshold(some_img, 255,
                                   cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY,
                                   21,
                                   0)
    return thresh


# Apply dilation
def dilate(some_img):
    # print("Dilating Image...")
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
    dilated = cv2.dilate(some_img, kernel)
    return dilated


# Apply Otsu threshold
def otsu_threshold(some_img):
    # print("Otsu Thresholding...")
    ret2, thresh2 = cv2.threshold(some_img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    return thresh2


def segmentation(some_img):
    gray_img = cv2.cvtColor(some_img, cv2.COLOR_BGR2GRAY)

    thresh1 = adaptive_threshold(gray_img)
    # print("Showing Thresholded image:")
    # show_image(thresh1)

    dilated = dilate(thresh1)
    # print("Showing dilated image:")
    # show_image(dilated)

    # print("Showing OTSU inverted image:")
    thresh2 = otsu_threshold(dilated)
    # show_image(thresh2)

    dilated2 = dilate(thresh2)
    # print("Showing dilated image (2):")
    # show_image(dilated2)

    return dilated2


# Check if contour fits the card properties
def isCardRect(x1, y1, w1, h1, hull_list):
    min_area = 110000
    max_area = 135000
    test_area = w1 * h1
    # print("Card Area:", test_area)
    if test_area >= max_area or test_area <= min_area:  # Filter large bounding rectangles
        # print("Contour not possible.")
        return False

    for hull in hull_list:
        dist1 = cv2.pointPolygonTest(hull, (x1, y1), False)
        dist2 = cv2.pointPolygonTest(hull, (x1 + w1, y1 + h1), False)
        if dist1 == 1 or dist2 == 1:
            # print("Not added - rect inside another rect")
            return False

    return True
