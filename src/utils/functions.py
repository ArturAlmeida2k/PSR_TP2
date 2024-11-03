#  ------------------------------
#  -----      Imports       -----
#  ------------------------------
import cv2
import numpy as np
import random
from colorama import Style, Fore



#  ------------------------------
#  -----  Helper Functions  -----
#  ------------------------------

# Captura de vídeo
def start_video_capture():

    cap = cv2.VideoCapture(0)  
    
    # Verificar se a câmara abriu corretamente
    if not cap.isOpened():
        print("Erro: Não foi possível abrir a câmara.")
        exit()

    return cap

# Criar uma tela em branco com o mesmo tamanho da captura de vídeo
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

# Sobrepor a tela e a captura de vídeo
def video_canvas(canvas, frame):
    # Tornar o background do canvas preto para poder fazer cv2.add() 
    canvas[np.all(canvas == [255, 255, 255], axis=-1)] = [0, 0, 0]
    
    # Armazenar onde exite cor vermelha|verde|azul para quando se juntar o frame não somar valores aos 0's
    red_mask = np.all(canvas == [0, 0, 255], axis=-1)
    green_mask = np.all(canvas == [0, 255, 0], axis=-1)
    blue_mask = np.all(canvas == [255, 0, 0], axis=-1)
    color_mask = red_mask | green_mask | blue_mask
    
    canvas_frame = np.where(color_mask[..., None], canvas, cv2.add(frame, canvas))
    return canvas_frame

# Importar uma imagem para colorir
def number_image(height, width, image_path):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    image = cv2.resize(image, (int(image.shape[1] * height / image.shape[0]), height))

    ret, thresh = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    image = np.zeros((height, width)).astype(np.uint8)
    image[:, int(width / 2 - thresh.shape[1] / 2):int(width / 2 + thresh.shape[1] / 2)] = thresh

    # Usar connectedComponentWithStats para encontrar os espaços em branco
    output = cv2.connectedComponentsWithStats(image, 4, cv2.CV_32S)

    num_labels = output[0]  # Número da área
    centroids = output[3]   # Centro da área


    # Escrever os números nos vários espaços em branco
    labelColors = [None] * num_labels
    fontScale = (width * height) / (650 * 650) / 2
    cv2.putText(image,
                str(1),
                (345, 205),
                cv2.FONT_HERSHEY_COMPLEX_SMALL,
                fontScale,
                (0, 0, 0),
                2)
    for i in range(2, len(centroids)):
        if labelColors[i] != (0, 0, 0) and (int(centroids[i][0] - fontScale * 14), int(centroids[i][1] + fontScale * 14)) != (627, 363):
            cv2.putText(image,
                        str(2),
                        (int(centroids[i][0] - fontScale * 14), int(centroids[i][1] + fontScale * 14)),
                        cv2.FONT_HERSHEY_COMPLEX_SMALL,
                        fontScale,
                        (0, 0, 0),
                        2)
        else:
            cv2.putText(image,
                        str(3),
                        (int(centroids[i][0] - fontScale * 14), int(centroids[i][1] + fontScale * 14)),
                        cv2.FONT_HERSHEY_COMPLEX_SMALL,
                        fontScale,
                        (0, 0, 0),
                        2)

    image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)

    return image

# Desenhar formas
def handle_shapes(k, pressing_s, pressing_o, engaged, let_go_sum, canvas, temp_canvas):
    # Caso ainda não esteja a registar varios valor para k continuos para e se esteja a mostrar uma forma
    # for criada isto para dar mais tempo de espera ate que registe os valores corretos para k
    if not engaged:
        if k == -1:
            let_go_sum += 1
            # Se registar até 5 valores que não sejam os esperados desenha a forma imediatamente
            if let_go_sum >= 5:
                pressing_s = False
                pressing_o = False
                canvas = temp_canvas.copy()
                let_go_sum = 0
        # Se registar um valor esperado torna engaged True e a partir de agora basta registar
        # Valores para desenhar a forma
        elif k == ord("s") or k == ord("S") or k == ord("o") or k == ord("O"):
            engaged = True
            let_go_sum = 0

    # Estando engaged, ao fim de 2 momentos com o k diferente do botão que devia ser precionado
    # a forma é desenhada 
    elif engaged:
        if pressing_s and not (k == ord("s") or k == ord("S")):
            let_go_sum += 1
            if let_go_sum >= 2:
                pressing_s = False
                engaged = False
                canvas = temp_canvas.copy()
                let_go_sum = 0
        elif pressing_o and not (k == ord("o") or k == ord("O")):
            let_go_sum += 1
            if let_go_sum >= 2:
                pressing_o = False
                engaged = False
                canvas = temp_canvas.copy()
                let_go_sum = 0
        else:
            let_go_sum = 0
    
    return pressing_s, pressing_o, engaged, let_go_sum, canvas

#
def evaluate_painting(painted_img):
    output = cv2.connectedComponentsWithStats(painted_img, 4, cv2.CV_32S)
    num_labels = output[0]  # Número da área
    labels = output[1]  # label matrix

    labelColors = [None] * num_labels

    hits = 0
    misses = 0

    for i in range(painted_img[1]):
        for j in range(painted_img[1]):
            rightColor = labelColors[labels[i, j]]
            if rightColor != (0, 0, 0):
                if np.array_equal(painted_img[i, j], rightColor):
                    hits += 1
                else:
                    misses += 1

    precision = str(round(hits / (hits + misses), 3))

    return precision