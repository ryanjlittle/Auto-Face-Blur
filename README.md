# Automatic Face Blurring

Before posting a photo containing other people online, it's important to respect the privacy of anyone in the photo who hasn't given consent to post it. This script automatically detects all faces present in an image and lets the user select which faces to expose--all non-exposed faces will be blurred. Automatic face is done using [MTCNN](https://pypi.org/project/mtcnn/). The script can also be run in manual mode, allowing the user to click and drag to select regions of the image to blur.

#### 1. Original Photo
<img src="https://github.com/ryanjlittle/Face-Blur/blob/main/images/original.jpg?raw=true" alt="original image" width="500"/>

#### 2. Faces are automatically detected
<img src="https://github.com/ryanjlittle/Face-Blur/blob/main/images/facesdetected.jpg?raw=true" alt="original image" width="500"/>

#### 3. User selects faces to expose
<img src="https://github.com/ryanjlittle/Face-Blur/blob/main/images/facesselected.jpg?raw=true" alt="original image" width="500"/>

#### 4. Blurred photo 
<img src="https://github.com/ryanjlittle/Face-Blur/blob/main/images/blurred.jpg?raw=true" alt="original image" width="500"/>

## Usage
```
$ python faceblur.py [-h] [-m] [-o OUT] IMAGE

positional arguments:
  IMAGE              Image to blur

optional arguments:
  -h, --help         show this help message and exit
  -m, --manual       Manually select faces
  -o OUT, --out OUT  Output file destination
```
