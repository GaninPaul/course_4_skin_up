
# import the necessary packages
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.models import load_model
import numpy as np
import argparse
import cv2
import os
from matplotlib import pyplot as plt


class AcnesObj():
    def __init__(self, filename, acne, withoutAcne):
        self.filename = filename
        self.acne = acne
        self.withoutAcne = withoutAcne

    def __str__(self) -> str:
        return self.filename + str(self.acne) + str(self.withoutAcne)


def detect_acne(path, files):
    res = []
    for filename in files:
        try:
            # load our serialized face detector model from disk
            print("[INFO] loading face detector model...")
            prototxtPath = os.path.sep.join(
                ["utils/points/face_detector", "deploy.prototxt"])
            weightsPath = os.path.sep.join(["utils/points/face_detector",
                                            "res10_300x300_ssd_iter_140000.caffemodel"])
            net = cv2.dnn.readNet(prototxtPath, weightsPath)

            # load the face mask detector model from disk
            print("[INFO] loading face acne detector model...")
            model = load_model(
                "/Users/pganin/Documents/vkr/src/utils/points/facemodel.model")

            # load the input image from disk, clone it, and grab the image spatial
            # dimensions
            image = cv2.imread(path+filename)
            orig = image.copy()
            (h, w) = image.shape[:2]

            # construct a blob from the image
            blob = cv2.dnn.blobFromImage(image, 1.0, (300, 300),
                                         (104.0, 177.0, 123.0))

            # pass the blob through the network and obtain the face detections
            print("[INFO] computing face detections...")
            net.setInput(blob)
            detections = net.forward()

            # loop over the detections
            for i in range(0, detections.shape[2]):
                # extract the confidence (i.e., probability) associated with
                # the detection
                confidence = detections[0, 0, i, 2]

                # filter out weak detections by ensuring the confidence is
                # greater than the minimum confidence
                if confidence > 0.5:
                    # compute the (x, y)-coordinates of the bounding box for
                    # the object
                    box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                    (startX, startY, endX, endY) = box.astype("int")

                    # ensure the bounding boxes fall within the dimensions of
                    # the frame
                    (startX, startY) = (max(0, startX), max(0, startY))
                    (endX, endY) = (min(w - 1, endX), min(h - 1, endY))

                    # extract the face ROI, convert it from BGR to RGB channel
                    # ordering, resize it to 224x224, and preprocess it
                    face = image[startY:endY, startX:endX]
                    face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
                    face = cv2.resize(face, (224, 224))
                    face = img_to_array(face)
                    face = preprocess_input(face)
                    face = np.expand_dims(face, axis=0)

                    (acne, withoutAcne) = model.predict(face)[0]
                    print("acne, withoutAcne " +
                          str(acne)+" " + str(withoutAcne))
                    acneobj = AcnesObj(filename=filename,
                                       acne=acne, withoutAcne=withoutAcne)
                    # return acneobj
                    res.append(acneobj)
            # display the label and bounding box rectangle on the output
            # frame
            # cv2.putText(image, label, (startX, startY - 10),
            #             cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 2)
            # cv2.rectangle(image, (startX, startY), (endX, endY), color, 2)
        except Exception as e:
            acneobj = AcnesObj(filename=filename,
                               acne=0, withoutAcne=0)
            print("except: " + filename)
            print(e)
            res.append(acneobj)
    return res
    # show the output image
    # plt.imshow((cv2.cvtColor(image, cv2.COLOR_BGR2RGB)))
    # plt.show()


# print("--------")
# detect_acne("", ["examples/41aebaf6-9f05-418b-907c-4755f3c72e40/cropped/e6318ab8-e078-4fcf-a9a5-f3948d28e11fphoto_2023-04-2718.43.07.jpeg_face.png"])
