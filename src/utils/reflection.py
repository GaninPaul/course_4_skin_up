import cv2
import numpy as np


def select_object(window, color, img_copy):
    cv2.rectangle(img_copy, window[0], window[1], color, 2, cv2.LINE_AA)
    obj = img_copy[window[0][1]:window[1][1], window[0][0]:window[1][0]]
    return obj


def create_mask(img):
    saturation = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)[:, :, 1]
    blur = cv2.GaussianBlur(saturation, (3, 3), 0)
    thresh = 255 - cv2.threshold(blur, 60, 255, cv2.THRESH_BINARY)[1]
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.dilate(thresh, kernel, iterations=1)
    return mask


def calculate_area(img, mask, color):
    contours, _ = cv2.findContours(
        mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        contour_area = cv2.contourArea(contour)
        cv2.drawContours(img, [contour], -1, color, 2)

    try:
        return contour_area
    except:
        pass


def draw_contours(img, mask, parameters):
    counter = []

    contours, _ = cv2.findContours(
        mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    param = parameters
    delta = 0.2

    for i in range(len(param)):
        for contour in contours:
            contour_area = cv2.contourArea(contour)

            try:
                if param[i][0] * (1 - delta) < contour_area < param[i][0] * (1 + delta):
                    cv2.drawContours(img, [contour], -1, param[i][1], 2)
                    counter.append(i)
            except:
                print(f"Object {i + 1} is not defined")

    # counter = {i: counter.count(i) for i in counter}

    return sum(counter)


def _detect_reflection(file, object_count):
    parameters = []
    image = cv2.imread(file)
    image_copy = image.copy()

    for i in range(object_count):
        obj_window = [(100, 100 + i * 100), (200, 200 + i * 100)]
        obj_color = (50, 100 + i * 70, 255)
        obj = select_object(obj_window, obj_color, image_copy)
        obj_mask = create_mask(obj)
        obj_area = calculate_area(obj, obj_mask, obj_color)
        parameters.append([obj_area, obj_color])

    mask = create_mask(image)
    count = draw_contours(image, mask, parameters)
    print("count "+str(count))
    return count

class ReflectionObj():
    def __init__(self, filename, reflection_count):
        self.filename = filename
        self.reflection_count = reflection_count


def detect_reflection(path, files):
    res = []
    for filename in files:
        try:
            reflection_count = _detect_reflection(
                path+filename, object_count=4)
            reflections = ReflectionObj(
                filename=filename, reflection_count=reflection_count)
            res.append(reflections)
        except Exception as e:
            reflections = ReflectionObj(filename=filename, reflection_count=0)
            print("except: "+path+filename + " 0")
            print("Exception"+e)
            res.append(reflections)
    return res
