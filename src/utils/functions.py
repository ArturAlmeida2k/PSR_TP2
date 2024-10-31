#  ------------------------------
#  -----      Imports       -----
#  ------------------------------
import cv2
import numpy as np



#  ------------------------------
#  -----  Helper Functions  -----
#  ------------------------------
    #Start video captue
def start_video_capture():

    cap = cv2.VideoCapture(0)  
    
    # Verify if the camera has been open correctly
    if not cap.isOpened():
        print("Erro: Não foi possível abrir a câmara.")
        exit()

    return cap

    #Create a blank canvas with the same size as the video capture
def create_blank_canvas(width, height):

    canvas = np.ones(shape=[height, width, 3], dtype=np.uint8) 
    canvas.fill(255)
    return canvas

    # Find largest contour in the mask
def get_largest_contour(mask):
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # If not contour is found .i.e the mask if full black
    if len(contours) == 0:
        return None
    
    # Find largest countour
    largest_contour = max(contours, key=cv2.contourArea)
    
    return largest_contour

    # Find the centroid of the contour
def get_centroid(contour):
    M = cv2.moments(contour)
    
    if M["m00"] == 0:  
        return None
    
    # Calculate centroid
    cx = int(M["m10"] / M["m00"])
    cy = int(M["m01"] / M["m00"])
    
    return (cx, cy)

def video_canvas(canvas, frame):
    # Tonar o background do canvas preto para poder fazer cv2.add() 
    canvas[np.all(canvas == [255, 255, 255], axis=-1)] = [0, 0, 0]
    
    # Armazenar onde exitem a cor vermelha|verde|azul para quando se juntar a frame não somar valores aos 0's
    red_mask = np.all(canvas == [0, 0, 255], axis=-1)
    green_mask = np.all(canvas == [0, 255, 0], axis=-1)
    blue_mask = np.all(canvas == [255, 0, 0], axis=-1)
    color_mask = red_mask | green_mask | blue_mask
    
    canvas_frame = np.where(color_mask[..., None], canvas, cv2.add(frame, canvas))
    return canvas_frame

def canvas_figure_square(canvas, figure, centroid):
    pass
    