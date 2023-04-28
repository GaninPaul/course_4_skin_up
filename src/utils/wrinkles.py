

from PIL import Image
import cv2
import time
import numpy as np
from skimage.filters import frangi, gabor
from skimage import measure, morphology


def seam_search(image):
    b, g, r = cv2.split(image)
    sk_frangi_img = frangi(g, scale_range=(
        0, 1), scale_step=0.01, beta1=1.5, beta2=0.01)
    sk_frangi_img = morphology.closing(sk_frangi_img, morphology.disk(1))
    sk_gabor_img_1, sk_gabor_1 = gabor(g, frequency=0.35, theta=0)
    sk_gabor_img_2, sk_gabor_2 = gabor(g, frequency=0.35, theta=45)
    sk_gabor_img_3, sk_gabor_3 = gabor(g, frequency=0.35, theta=90)
    sk_gabor_img_4, sk_gabor_4 = gabor(g, frequency=0.35, theta=360)
    sk_gabor_img_1 = morphology.opening(sk_gabor_img_1, morphology.disk(2))
    sk_gabor_img_2 = morphology.opening(sk_gabor_img_2, morphology.disk(1))
    sk_gabor_img_3 = morphology.opening(sk_gabor_img_3, morphology.disk(2))
    sk_gabor_img_4 = morphology.opening(sk_gabor_img_4, morphology.disk(2))
    all_img = cv2.add(0.1 * sk_gabor_img_2, 0.9 * sk_frangi_img)
    all_img = morphology.closing(all_img, morphology.disk(1))
    _, all_img = cv2.threshold(all_img, 0.3, 1, 0)
    img1 = all_img
    bool_img = all_img.astype(bool)
    label_image = measure.label(bool_img)
    count = 0

    for region in measure.regionprops(label_image):
        if region.area < 10:  # or region.area > 700
            x = region.coords
            for i in range(len(x)):
                all_img[x[i][0]][x[i][1]] = 0
            continue
        if region.eccentricity > 0.98:
            count += 1
        else:
            x = region.coords
            for i in range(len(x)):
                all_img[x[i][0]][x[i][1]] = 0

    skel, distance = morphology.medial_axis(
        all_img.astype(int), return_distance=True)
    skels = morphology.closing(skel, morphology.disk(1))
    trans1 = skels
    return skels, count


def face_wrinkle(path):
    result = cv2.imread(path)
    img, count = seam_search(result)
    result[img > 0.5] = 255
    # print("c: "+result)

    # cv2.imshow("result", img.astype(float))
    # cv2.waitKey(0)
    return count


class WrinklesObj():
    def __init__(self, filename, wrinkles_count):
        self.filename = filename
        self.wrinkles_count = wrinkles_count


def face_wrinkles(path, files):
    res = []

    for filename in files:
        try:
            print("path+filename: "+path+filename)
            c = face_wrinkle(path+filename)
            wrinkles = WrinklesObj(filename=filename, wrinkles_count=c)
            print("path+filename: "+path+filename + "__" + str(c))

            res.append(wrinkles)
        except Exception as e:
            wrinkles = WrinklesObj(filename=filename, wrinkles_count=0)
            print("except: "+path+filename + " 0")
            print("Exception"+e)

            res.append(wrinkles)
    return res
