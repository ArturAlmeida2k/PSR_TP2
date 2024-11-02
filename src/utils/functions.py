#  ------------------------------
#  -----      Imports       -----
#  ------------------------------
import cv2
import numpy as np
import random



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
    
    # Armazenar onde exitem a cor vermelha|verde|azul para quando se juntar a frame não somar valores aos 0's
    red_mask = np.all(canvas == [0, 0, 255], axis=-1)
    green_mask = np.all(canvas == [0, 255, 0], axis=-1)
    blue_mask = np.all(canvas == [255, 0, 0], axis=-1)
    color_mask = red_mask | green_mask | blue_mask
    
    canvas_frame = np.where(color_mask[..., None], canvas, cv2.add(frame, canvas))
    return canvas_frame


# Importar uma imagem para colorir
def load_image(height, width):
    image = cv2.imread("./img/flor.png", cv2.IMREAD_GRAYSCALE)

    image = cv2.resize(image, (int(image.shape[1] * height / image.shape[0]), height))

    ret, thresh = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    image = np.zeros((height, width)).astype(np.uint8)

    image[:, int(width / 2 - thresh.shape[1] / 2):int(width / 2 + thresh.shape[1] / 2)] = thresh

    # Usar connectedComponentWithStats para encontrar os espaços em branco
    connectivity = 4
    output = cv2.connectedComponentsWithStats(image, connectivity, cv2.CV_32S)

    num_labels = output[0]  # Número da área
    labels = output[1]      # Legenda da área
    stats = output[2]       # Estatísticas
    centroids = output[3]   # Centro da área

    # Associar o número à cor
    colors = [(0, 0, 255), (0, 255, 0), (255, 0, 0)]
    labelColors = [None] * num_labels

    for i in range(height):
        for j in range(width):
            if not labelColors[labels[i][j]]:
                if image[i][j] == 0:
                    labelColors[labels[i][j]] = (0, 0, 0)
                else:
                    labelColors[labels[i][j]] = colors[random.randint(0,2)]

    # Escrever os números nos vários espaços em branco
    fontScale = (width * height) / (800 * 800) / 2
    for i in range(0, len(centroids)):
        if labelColors[i] != (0, 0, 0):
            cv2.putText(image, str(i), (int(centroids[i][0] - fontScale * 14), int(centroids[i][1] + fontScale * 14)), cv2.FONT_HERSHEY_COMPLEX_SMALL, fontScale, (0, 0, 0), 1)

    image = cv2.bitwise_not(image)

    return cv2.cvtColor(image, cv2.COLOR_GRAY2RGB), labelColors, labels