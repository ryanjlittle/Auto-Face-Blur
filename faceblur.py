from itertools import compress
from os import path
from mtcnn.mtcnn import MTCNN as mtcnn
import cv2
import argparse 
    
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
    return [face["box"] for face in faces] 

def manually_select_faces(img):
    img_copy = img.copy()
    cv2.imshow("Image", img_copy)
    cv2.setMouseCallback("Image", select_faces_event_handler, img_copy)
    cv2.waitKey(0)
    return faces
    

def choose_faces(img, faces):
    faces_to_blur = [True] * len(faces) # Indicates if each face should be blurred. True by default.
    img_copy = img.copy()
    for x, y, w, h in faces:
        #cv2.rectangle(img_copy, (x,y), (x+w, y+h), (0,0,255), 2)
        center = (int(x+w/2), int(y+h/2))
        axes = (int(w/2), int(h/2))
        cv2.ellipse(img_copy, center, axes, 0, 0, 360, (0,0,255), 2)
    
    print("Click on all faces you wish to expose. When done selecting, press any key to process the image.")
    cv2.imshow("Image", img_copy)
    cv2.setMouseCallback("Image", select_faces_to_blur_event_handler, (img_copy, faces, faces_to_blur))
    cv2.waitKey(0)

    return list(compress(faces, faces_to_blur))

def select_faces_to_blur_event_handler(event, click_x, click_y, flags, params):
    global faces_to_blur
    image, faces, faces_to_blur = params
    if event == cv2.EVENT_LBUTTONDOWN:
        for face, blur, i in zip(faces, faces_to_blur, range(len(faces))):
            x, y, w, h = face
            if x <= click_x <= x + w and y <= click_y <= y + h:
                color = (0,255,0) if blur else (0,0,255)
                #cv2.rectangle(img, (x,y), (x+w, y+h), color, 2)
                center = (int(x+w/2), int(y+h/2))
                axes = (int(w/2), int(h/2))
                cv2.ellipse(img, center, axes, 0, 0, 360, color, 2)
                faces_to_blur[i] = not faces_to_blur[i]


def select_faces_event_handler(event, x, y, flags, img):
    global selecting_face, faces, x_orig, y_orig
    if event == cv2.EVENT_LBUTTONDOWN:
        selecting_face = True
        x_orig, y_orig = x, y

    elif event == cv2.EVENT_MOUSEMOVE:
        if selecting_face:
            img_copy = img.copy()
            #cv2.rectangle(img_copy, (x_orig,y_orig), (x, y), (0,0,255), 2)
            center = (int((x_orig+x)/2), int((y_orig+y)/2))
            axes = (abs(int((x_orig-x)/2)), abs(int((y_orig-y)/2)))
            cv2.ellipse(img_copy, center, axes, 0, 0, 360, (0,0,255), 2)
            cv2.imshow("Image", img_copy)
        
    elif event == cv2.EVENT_LBUTTONUP:
        if selecting_face:
            img_copy = img.copy()
            #cv2.rectangle(img, (x_orig,y_orig), (x, y), (0,0,255), 2)
            center = (int((x_orig+x)/2), int((y_orig+y)/2))
            axes = (abs(int((x_orig-x)/2)), abs(int((y_orig-y)/2)))
            cv2.ellipse(img, center, axes, 0, 0, 360, (0,0,255), 2)
            new_x = min(x_orig, x)
            new_y = min(y_orig, y)
            w = abs(x_orig-x)
            h = abs(y_orig-y)
            faces += [(new_x,new_y,w,h)]
            draw_face_borders(img, faces)
            selecting_face = False

    elif event == cv2.EVENT_RBUTTONDOWN:
        print(faces)
        for i, (face_x, face_y, w, h) in enumerate(faces):
            if face_x <= x <= face_x + w and face_y <= y <= face_y + h:
                faces.pop(i)
        draw_face_borders(img, faces)

def draw_face_borders(img, faces):
    img_copy = img.copy()
    for (x,y,w,h) in faces:
        center = (int(x+w/2), int(y+h/2))
        axes = (int(w/2), int(h/2))
        cv2.ellipse(img_copy, center, axes, 0, 0, 360, (0,0,255), 2)
    cv2.imshow("Image", img_copy)

def blur_faces(img, faces):
    for x, y, w, h in faces:
        img[y:y+h, x:x+w] = cv2.blur(img[y:y+h, x:x+w], (30,30)) 

if __name__ == "__main__":
    parser = make_parser()
    args = parser.parse_args()

    img_path = args.image
    img = cv2.imread(img_path)

    if args.manual:
        faces = manually_select_faces(img)
    else:
        faces = auto_detect_faces(img)
        faces = choose_faces(img, faces)

    print(faces)
    
    blur_faces(img, faces)

    if args.out:
        out_path = args.out
    else:
        name, ext = path.splitext(path.basename(img_path))
        out_path = name + "_BLURRED" + ext

    cv2.imwrite(out_path, img)
    cv2.imshow("Blurred Image", img)
    cv2.waitKey(0)

    print("Image saved to", out_path)

    cv2.destroyAllWindows()
    

