import mediapipe as mp
import cv2
import numpy as np
import os

mp_selfie_segmentation = mp.solutions.selfie_segmentation
mp_drawing = mp.solutions.drawing_utils
mp_face_mesh = mp.solutions.face_mesh


def _crop_face(image, face_landmarks):
    xs = [landmark.x * image.shape[1] for landmark in face_landmarks]
    ys = [landmark.y * image.shape[0] for landmark in face_landmarks]

    min_x, max_x = int(min(xs)), int(max(xs))
    min_y, max_y = int(min(ys)), int(max(ys))

    cropped_image = image[min_y-90:max_y+10, min_x-30:max_x+30]

    return cropped_image


BG_COLOR = (192, 192, 192)


def crop_face(path, files):
    for filename in files:
        try:
            with mp_face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5) as face_mesh:
                with mp_selfie_segmentation.SelfieSegmentation(model_selection=1) as selfie_segmentation:
                    image = cv2.imread(path+filename)
                    bg_image = None
                    image = cv2.flip(image, 1)
                    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

                    results = face_mesh.process(image_rgb)
                    results2s = selfie_segmentation.process(image_rgb)

                    condition = np.stack(
                        (results2s.segmentation_mask,) * 3, axis=-1) > 0.9
                    if bg_image is None:
                        bg_image = np.zeros(image.shape, dtype=np.uint8)
                        bg_image[:] = BG_COLOR
                    output_image = np.where(condition, image, bg_image)

                    if results.multi_face_landmarks:
                        for face_landmarks in results.multi_face_landmarks:
                            cropped_image = _crop_face(
                                output_image, face_landmarks.landmark)
                            print(path+"cropped/"+filename +
                                  '.png')
                            cv2.imwrite(path+"cropped/"+filename +
                                        '.png', cropped_image)
                            # saveTriangles(cropped_image)
                    cv2.imwrite(path+"cropped/"+filename +
                                '_face.png', output_image)
        except:
            print("except: "+path+filename)
            image = cv2.imread(path+filename)
            cv2.imwrite(path+"cropped/"+filename+'_face.png', image)
