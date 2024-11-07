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
    limits = {"H": {"max": 179, "min": 0}, "S": {"max": 255, "min": 0}, "V": {"max": 255, "min": 0}}

    _, frame = capture.read()
    cv2.createTrackbar("H-min", window_name, limits["H"]["min"], 179, lambda threshold: onTrackbar(threshold, mm="min", C="H", limits=limits))
    cv2.createTrackbar("H-max", window_name, limits["H"]["max"], 179, lambda threshold: onTrackbar(threshold, mm="max", C="H", limits=limits))
    cv2.createTrackbar("S-min", window_name, limits["S"]["min"], 255, lambda threshold: onTrackbar(threshold, mm="min", C="S", limits=limits))
    cv2.createTrackbar("S-max", window_name, limits["S"]["max"], 255, lambda threshold: onTrackbar(threshold, mm="max", C="S", limits=limits))
    cv2.createTrackbar("V-min", window_name, limits["V"]["min"], 255, lambda threshold: onTrackbar(threshold, mm="min", C="V", limits=limits))
    cv2.createTrackbar("V-max", window_name, limits["V"]["max"], 255, lambda threshold: onTrackbar(threshold, mm="max", C="V", limits=limits))
    
    while (True):
        _, frame = capture.read() 

        hsv_frame = cv2.cvtColor(cv2.flip(frame,1),cv2.COLOR_BGR2HSV)

        mask = cv2.inRange(hsv_frame,(limits["H"]["min"], limits["S"]["min"], limits["V"]["min"]),(limits["H"]["max"], limits["S"]["max"], limits["V"]["max"]))
        cv2.imshow(window_name, mask)

        k = cv2.waitKey(1)

        if k == ord("q") or k == ord("Q"):
            break
        elif k == ord("w") or k == ord("W"):
            file_name = "limits.json"
            with open(file_name, 'w') as json_file:
                print("writing dictionary d to file " + file_name)
                print( "           VALUES        ")
                print(f" H -> min: {limits['H']['min']:3}| max: {limits['H']['max']:3}")
                print(f" S -> min: {limits['S']['min']:3}| max: {limits['S']['max']:3}")
                print(f" V -> min: {limits['V']['min']:3}| max: {limits['V']['max']:3}")
                json.dump({"limits": limits}, json_file, indent=4)


if __name__ == '__main__':
    main()