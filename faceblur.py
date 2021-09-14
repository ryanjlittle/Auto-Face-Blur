from itertools import compress
from os import path
import cv2
import numpy as np
import argparse 
from mtcnn.mtcnn import MTCNN as mtcnn
    
faces = []
selecting_face = False

def make_parser():
    parser = argparse.ArgumentParser("Blur faces in an image to preserve privacy!")
    parser.add_argument("image", help="Image to blur")
    parser.add_argument("-m", "--manual", action="store_true", help="Manually select faces")
    parser.add_argument("-o", "--out", type=str, help="Output file destination")
    return parser


def auto_detect_faces(img):
    detector = mtcnn()
    faces = detector.detect_faces(img)
    faces = [face["box"] for face in faces] 
    return choose_faces(img, faces)

def manually_select_faces(img):
    print("Click and drag to select regions to blur. When done, press any key to process the image.")
    img_copy = img.copy()
    cv2.imshow("Image", img_copy)
    cv2.setMouseCallback("Image", select_faces_event_handler, img_copy)
    cv2.waitKey(0)
    return faces
    

def choose_faces(img, faces):
    print("\n\nClick on all faces you wish to expose. When done, press any key to process the image.")
    faces_to_blur = [True] * len(faces) # Indicates if each face should be blurred. True by default.
    img_copy = img.copy()
    for x, y, w, h in faces:
        center = (int(x+w/2), int(y+h/2))
        axes = (int(w/2), int(h/2))
        cv2.ellipse(img_copy, center, axes, 0, 0, 360, (0,0,255), 2)
    
    cv2.imshow("Image", img_copy)
    cv2.setMouseCallback("Image", select_faces_to_blur_event_handler, (img_copy, faces, faces_to_blur))
    cv2.waitKey(0)

    return list(compress(faces, faces_to_blur))


def select_faces_event_handler(event, x, y, flags, img):
    global selecting_face, faces, x_orig, y_orig
    if event == cv2.EVENT_LBUTTONDOWN:
        selecting_face = True
        x_orig, y_orig = x, y

    elif event == cv2.EVENT_MOUSEMOVE:
        if selecting_face:
            img_copy = img.copy()
            center = (int((x_orig+x)/2), int((y_orig+y)/2))
            axes = (abs(int((x_orig-x)/2)), abs(int((y_orig-y)/2)))
            cv2.ellipse(img_copy, center, axes, 0, 0, 360, (0,0,255), 2)
            cv2.imshow("Image", img_copy)
        
    elif event == cv2.EVENT_LBUTTONUP:
        if selecting_face:
            img_copy = img.copy()
            center = (int((x_orig+x)/2), int((y_orig+y)/2))
            axes = (abs(int((x_orig-x)/2)), abs(int((y_orig-y)/2)))
            cv2.ellipse(img, center, axes, 0, 0, 360, (0,0,255), 2)
            new_x = min(x_orig, x)
            new_y = min(y_orig, y)
            w = abs(x_orig-x)
            h = abs(y_orig-y)
            faces += [(new_x,new_y,w,h)]
            selecting_face = False


def select_faces_to_blur_event_handler(event, click_x, click_y, flags, params):
    global faces_to_blur
    image, faces, faces_to_blur = params
    if event == cv2.EVENT_LBUTTONDOWN:
        for face, blur, i in zip(faces, faces_to_blur, range(len(faces))):
            x, y, w, h = face
            if x <= click_x <= x + w and y <= click_y <= y + h:
                color = (0,255,0) if blur else (0,0,255)
                center = (int(x+w/2), int(y+h/2))
                axes = (int(w/2), int(h/2))
                cv2.ellipse(image, center, axes, 0, 0, 360, color, 2)
                faces_to_blur[i] = not faces_to_blur[i]
    cv2.imshow("Image", image)


def blur_faces(img, faces):
    img_copy = img.copy()
    mask_shape = (img.shape[0], img.shape[1], 1)
    mask = np.full(mask_shape, 0, dtype=np.uint8)
    for (x, y, w, h) in faces:
        img_copy[y:y+h, x:x+w] = cv2.blur(img_copy[y:y+h, x:x+w], (20,20)) 
        center = (int(x+w/2), int(y+h/2))
        axes = (int(w/2), int(h/2))
        cv2.ellipse(mask, center, axes, 0, 0, 360, 255, -1)

    mask_inv = cv2.bitwise_not(mask)
    background = cv2.bitwise_and(img, img, mask=mask_inv)
    foreground = cv2.bitwise_and(img_copy, img_copy, mask=mask)
    return cv2.add(background, foreground)


if __name__ == "__main__":
    parser = make_parser()
    args = parser.parse_args()

    img_path = args.image
    if args.out:
        out_path = args.out
    else:
        name, ext = path.splitext(path.basename(img_path))
        out_path = name + "_BLURRED" + ext

    img = cv2.imread(img_path)
    if args.manual:
        faces = manually_select_faces(img)
    else:
        faces = auto_detect_faces(img)

    img = blur_faces(img, faces)

    cv2.imwrite(out_path, img)
    print("Image saved to", out_path)
    cv2.imshow("Blurred Image", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

