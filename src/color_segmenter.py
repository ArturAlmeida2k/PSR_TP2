#!/usr/bin/env python3


import cv2
import json

def save(event,x,y,flags,param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print(x,y)

def onTrackbar(threshold, mm, C,limits):
    limits[C][mm] = threshold
    

def main():
    window_name = "Video"
    cv2.namedWindow(window_name)
    capture = cv2.VideoCapture(0)
    limits = {"B": {"max": 255, "min": 0},"G": {"max": 255, "min": 0},"R": {"max": 255, "min": 0}}
    ret, frame = capture.read() 
    #cv2.imshow(window_name,frame)
    cv2.createTrackbar("B-min",window_name,limits["B"]["min"],255,lambda threshold: onTrackbar(threshold, mm="min", C="B",limits=limits))
    cv2.createTrackbar("B-max",window_name,limits["B"]["max"],255,lambda threshold: onTrackbar(threshold, mm="max", C="B",limits=limits))
    cv2.createTrackbar("G-min",window_name,limits["G"]["min"],255,lambda threshold: onTrackbar(threshold, mm="min", C="G",limits=limits))
    cv2.createTrackbar("G-max",window_name,limits["G"]["max"],255,lambda threshold: onTrackbar(threshold, mm="max", C="G",limits=limits))
    cv2.createTrackbar("R-min",window_name,limits["R"]["min"],255,lambda threshold: onTrackbar(threshold, mm="min", C="R",limits=limits))
    cv2.createTrackbar("R-max",window_name,limits["R"]["max"],255,lambda threshold: onTrackbar(threshold, mm="max", C="R",limits=limits))

    
    while (True):
        ret, frame = capture.read() 

        mask = cv2.inRange(frame,(limits["B"]["min"],limits["G"]["min"],limits["R"]["min"]),(limits["B"]["max"],limits["G"]["max"],limits["R"]["max"]))       
        cv2.imshow(window_name,mask)

        k = cv2.waitKey(1)

        if k == ord("q"):
            break
        elif k == ord("w"):
            file_name = 'limits.json'
            with open(file_name, 'w') as json_file:
                print('writing dictionary d to file ' + file_name)
                json.dump({"limits": limits}, json_file, indent=4)

if __name__ == '__main__':
    main()