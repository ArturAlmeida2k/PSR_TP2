#  ------------------------------
#  -----      Imports       -----
#  ------------------------------
import cv2
import numpy as np



#  ------------------------------
#  -----  Helper Functions  -----
#  ------------------------------

# Captação de vídeo
def start_video_capture():

    cap = cv2.VideoCapture(0)  
    
    # Verificar se a câmara abriu corretamente
    if not cap.isOpened():
        print("Erro: Não foi possível abrir a câmara.")
        exit()

    return cap

# Criar uma tela em branco com o mesmo tamanho da captação de vídeo
def create_blank_canvas(width, height):

    canvas = np.ones(shape=[height, width, 3], dtype=np.uint8) 
    canvas.fill(255)
    return canvas

# Encontrar a maior máscara
def get_largest_contour(mask):
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Caso não encontre nenhum contorno (ex.: a máscara ser toda preta)
    if len(contours) == 0:
        return None
    
    # Encontrar a maior máscara
    largest_contour = max(contours, key=cv2.contourArea)
    
    return largest_contour

# Encontrar o centro da máscara
def get_centroid(contour):
    M = cv2.moments(contour)
    
    if M["m00"] == 0:  
        return None
    
    # Calcular o centro
    cx = int(M["m10"] / M["m00"])
    cy = int(M["m01"] / M["m00"])
    
    return (cx, cy)

def video_canvas(canvas, frame):
    # Tornar o background do canvas preto para poder fazer cv2.add() 
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
    