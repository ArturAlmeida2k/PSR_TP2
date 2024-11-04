#!/usr/bin/env python3


import cv2
import json

def save(event,x,y):
    if event == cv2.EVENT_LBUTTONDOWN:
        print(x,y)

def onTrackbar(threshold, mm, C,limits):
    limits[C][mm] = threshold


# Recolher os valores para a segmentação de cor
def main():
    window_name = "Segmentacao de Cor"
    cv2.namedWindow(window_name)
    capture = cv2.VideoCapture(0)
    limits = {"B": {"max": 100, "min": 0},"G": {"max": 100, "min": 0},"R": {"max": 360, "min": 0}}
    # limits = {"B": {"max": 255, "min": 0},"G": {"max": 255, "min": 0},"R": {"max": 255, "min": 0}}
    _, frame = capture.read()
    cv2.createTrackbar("V-min",window_name,limits["B"]["min"],100,lambda threshold: onTrackbar(threshold=int((threshold/100)*255), mm="min", C="B",limits=limits))
    cv2.createTrackbar("V-max",window_name,limits["B"]["max"],100,lambda threshold: onTrackbar(threshold=int((threshold/100)*255), mm="max", C="B",limits=limits))
    cv2.createTrackbar("S-min",window_name,limits["G"]["min"],100,lambda threshold: onTrackbar(threshold=int((threshold/100)*255), mm="min", C="G",limits=limits))
    cv2.createTrackbar("S-max",window_name,limits["G"]["max"],100,lambda threshold: onTrackbar(threshold=int((threshold/100)*255), mm="max", C="G",limits=limits))
    cv2.createTrackbar("H-min",window_name,limits["R"]["min"],360,lambda threshold: onTrackbar(threshold=int((threshold/360)*255), mm="min", C="R",limits=limits))
    cv2.createTrackbar("H-max",window_name,limits["R"]["max"],360,lambda threshold: onTrackbar(threshold=int((threshold/360)*255), mm="max", C="R",limits=limits))
    '''
    cv2.createTrackbar("B-min",window_name,limits["B"]["min"],255,lambda threshold: onTrackbar(threshold, mm="min", C="B",limits=limits))
    cv2.createTrackbar("B-max",window_name,limits["B"]["max"],255,lambda threshold: onTrackbar(threshold, mm="max", C="B",limits=limits))
    cv2.createTrackbar("G-min",window_name,limits["G"]["min"],255,lambda threshold: onTrackbar(threshold, mm="min", C="G",limits=limits))
    cv2.createTrackbar("G-max",window_name,limits["G"]["max"],255,lambda threshold: onTrackbar(threshold, mm="max", C="G",limits=limits))
    cv2.createTrackbar("R-min",window_name,limits["R"]["min"],255,lambda threshold: onTrackbar(threshold, mm="min", C="R",limits=limits))
    cv2.createTrackbar("R-max",window_name,limits["R"]["max"],255,lambda threshold: onTrackbar(threshold, mm="max", C="R",limits=limits))
    '''

    while (True):
        _, frame = capture.read() 

        mask = cv2.inRange(cv2.flip(frame, 1),(limits["B"]["min"],limits["G"]["min"],limits["R"]["min"]),(limits["B"]["max"],limits["G"]["max"],limits["R"]["max"]))
        cv2.imshow(window_name, mask)

        k = cv2.waitKey(1)

        if k == ord("q") or k == ord("Q"):
            break
        elif k == ord("w") or k == ord("W"):
            file_name = 'limits.json'
            with open(file_name, 'w') as json_file:
                print('writing dictionary d to file ' + file_name)
                json.dump({"limits": limits}, json_file, indent=4)


if __name__ == '__main__':
    main()