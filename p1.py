import cv2 
import numpy as np
import argparse

def apply_brightness_contrast(input_img, brightness = 0, contrast = 0):

    if brightness != 0:
        if brightness > 0:
            shadow = brightness
            highlight = 255
        else:
            shadow = 0
            highlight = 255 + brightness
        alpha_b = (highlight - shadow)/255
        gamma_b = shadow

        buf = cv2.addWeighted(input_img, alpha_b, input_img, 0, gamma_b)
    else:
        buf = input_img.copy()

    if contrast != 0:
        f = 131*(contrast + 127)/(127*(131-contrast))
        alpha_c = f
        gamma_c = 127*(1-f)

        buf = cv2.addWeighted(buf, alpha_c, buf, 0, gamma_c)

    return buf

# Read image given by user
cap=cv2.VideoCapture("Night Drive - 2689.mp4")
flag=1 

while 1:
    ret,frame=cap.read()

    if frame is None:
        break
    
    
    img = frame  

    s = int(512*3/4)
    img = cv2.resize(img, (s,s), 0, 0, cv2.INTER_AREA)
    
    
    
    
    
    
    out= apply_brightness_contrast(img, 128, 80)
    

        
    cv2.imshow('out',out)
    cv2.imshow('frame',frame)

    

    gamma=1.5
	
	
    invGamma=1/gamma
    table=np.array([((i/255)**invGamma)*255 for i in np.arange(0,256)]).astype("uint8")

	
    
    gamma_transform=cv2.LUT(out, table)
    
    cv2.imshow("gamma",gamma_transform)

    
    
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()
