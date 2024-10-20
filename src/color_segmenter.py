import cv2
from functools import partial
from readchar import key

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
    cv2.createTrackbar("B-min",window_name,limits["B"]["min"],255,partial(onTrackbar, mm="min", C="B",limits=limits))
    cv2.createTrackbar("B-max",window_name,limits["B"]["max"],255,partial(onTrackbar, mm="max", C="B",limits=limits))
    cv2.createTrackbar("G-min",window_name,limits["G"]["min"],255,partial(onTrackbar, mm="min", C="G",limits=limits))
    cv2.createTrackbar("G-max",window_name,limits["G"]["max"],255,partial(onTrackbar, mm="max", C="G",limits=limits))
    cv2.createTrackbar("R-min",window_name,limits["R"]["min"],255,partial(onTrackbar, mm="min", C="R",limits=limits))
    cv2.createTrackbar("R-max",window_name,limits["R"]["max"],255,partial(onTrackbar, mm="max", C="R",limits=limits))

    
    while (True):
        ret, frame = capture.read()   
        mask = cv2.inRange(frame,(limits["B"]["min"],limits["G"]["min"],limits["R"]["min"]),(limits["B"]["max"],limits["G"]["max"],limits["R"]["max"]))       

        cv2.imshow(window_name,mask)

        # add code to create the trackbar ...
        if cv2.waitKey(1) == ord("q"):
            break

if __name__ == '__main__':
    main()