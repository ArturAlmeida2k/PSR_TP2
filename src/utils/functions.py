#  ------------------------------
#  -----      Imports       -----
#  ------------------------------
import cv2
import numpy as np
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

# Mostrar como foi inicializado o programa
def program_initialization(shake, videocanva, coloringimage, evaluation):
    print("Programa inicializado com os seguintes parametros:")

    if shake:
        color = Fore.GREEN
    else:
        color = Fore.RED
    print("Shake Prevention:",color,shake,Style.RESET_ALL)

    if videocanva:
        color = Fore.GREEN
    else:
        color = Fore.RED
    print("Video Canva:",color,videocanva,Style.RESET_ALL)

    if coloringimage:
        color = Fore.GREEN
    else:
        color = Fore.RED
    print("Coloring Image:",color,coloringimage,Style.RESET_ALL)

    if coloringimage:

        if evaluation:
            color = Fore.GREEN
        else:
            color = Fore.RED
        print("Evaluation:",color,evaluation, Style.RESET_ALL)

        if evaluation:
            print("A precisão de pintura seŕa realizada ao salvar a imagem (w)")
        print(Style.BRIGHT + "\nCores para pintar a imagem:" + Style.RESET_ALL)
        print(Fore.GREEN + "\tVerde: " + Style.RESET_ALL + "1")
        print(Fore.RED + "\tVermelho: " + Style.RESET_ALL + "2")
        print(Fore.BLUE + "\tAzul: " + Style.RESET_ALL + "3\n")
    
    if evaluation and not coloringimage:
        print(Fore.RED + "Não é possivel fazer a precisão da pintura se o programa não for iniciado com uma imagem para colorir" + Style.RESET_ALL)
        
    print("Precione 'h' para ver os comandos disponíveis")

# Mostra todos os comandos possiveis    
def print_commands():
    print("Comandos disponíveis:")
    print("R/r - Muda a cor do lápis para vermelho.")
    print("G/g - Muda a cor do lápis para verde.")
    print("B/b - Muda a cor do lápis para azul.")
    print("+ - Aumenta a grossura do lápis (máximo 25).")
    print("- - Diminui a grossura do lápis (mínimo 1).")
    print("C/c - Limpa a tela.")
    print("W/w - Salva a imagem atual.")
    print("S/s - Inicia uma ação específica relacionada à maior contorno, se aplicável.")
    print("O/o - Inicia outra ação específica relacionada à maior contorno, se aplicável.")
    print("H/h - Mostra a lista de comandos disponíveis.")
    print("Q/q - Fecha o programa.\n\n")
    

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

    black_mask = np.all(canvas == [0,0,0], axis=-1)

    # Tornar o background do canvas preto para poder fazer cv2.add() 
    canvas[np.all(canvas == [255, 255, 255], axis=-1)] = [0, 0, 0]
    
    # Armazenar onde exite cor vermelha|verde|azul para quando se juntar o frame não somar valores aos 0's
    red_mask = np.all(canvas == [0, 0, 255], axis=-1)
    green_mask = np.all(canvas == [0, 255, 0], axis=-1)
    blue_mask = np.all(canvas == [255, 0, 0], axis=-1)
    color_mask = black_mask | red_mask | green_mask | blue_mask
    
    canvas_frame = np.where(color_mask[..., None], canvas, cv2.add(frame, canvas))
    return canvas_frame


# Desenhar formas
def handle_shapes(k, pressing_s, pressing_o, engaged, let_go_sum, canvas, temp_canvas):
    # Caso ainda não esteja a registar varios valor para k continuos para e se esteja a mostrar uma forma
    # for criada isto para dar mais tempo de espera ate que registe os valores corretos para k
    
    
    if not engaged:
        if k == -1:
            let_go_sum += 1
            # Se registar até 5 valores que não sejam os esperados desenha a forma imediatamente
            if let_go_sum >= 20:
                pressing_s = False
                pressing_o = False
                canvas = temp_canvas.copy()
                let_go_sum = 0
        # Se registar um valor esperado torna engaged True e a partir de agora basta registar
        # Valores para desenhar a forma
        elif k == ord("s") or k == ord("S") or k == ord("o") or k == ord("O"):
            engaged = True
            let_go_sum = 0

    # Estando engaged, ao fim de 2 momentos com o k diferente do botão que devia ser precionado, a forma é desenhada 
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


# Importar uma imagem para colorir
def blank_coloring_image(height, width, image_path):

    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    image = cv2.resize(image, (int(image.shape[1] * height / image.shape[0]), height))

    _, thresh = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    image = np.zeros((height, width)).astype(np.uint8)
    image.fill(255)

    image[:, int(width / 2 - thresh.shape[1] / 2):int(width / 2 + thresh.shape[1] / 2)] = thresh

    # Usar connectedComponentWithStats para encontrar os espaços em branco
    num_labels, _, _, centroids = cv2.connectedComponentsWithStats(image, 4, cv2.CV_32S)

    # Escrever os números nos vários espaços em branco
    labelColors = [None] * num_labels
    fontScale = (width * height)/(350*350)/2
    thickness = 2
    for i in range(1, len(centroids)):
        if labelColors[i] != (0, 0, 0) and i == 1:
            cv2.putText(image,
                        str(i),
                        (85, 100),
                        cv2.FONT_HERSHEY_COMPLEX_SMALL,
                        fontScale,
                        (0, 0, 0),
                        thickness)
        elif labelColors[i] != (0, 0, 0) and i != 5:
            cv2.putText(image,
                        str(2),
                        (int(centroids[i][0] - fontScale * 7.5), int(centroids[i][1] + fontScale * 7.5)),
                        cv2.FONT_HERSHEY_COMPLEX_SMALL,
                        fontScale,
                        (0, 0, 0),
                        thickness)
        else:
            cv2.putText(image,
                        str(3),
                        (int(centroids[i][0] - fontScale * 7.5), int(centroids[i][1] + fontScale * 7.5)),
                        cv2.FONT_HERSHEY_COMPLEX_SMALL,
                        fontScale,
                        (0, 0, 0),
                        thickness)

    image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)

    return image


# Função para vereficar a precisão de pintura
def evaluate_coloring_image(image, image_path):
    
    control_image = cv2.imread(image_path, cv2.IMREAD_COLOR)

    height, width, _ = image.shape

    # Converter a imagem para porpuções iguais
    control_image = cv2.resize(control_image, (int(control_image.shape[1] * height / control_image.shape[0]), height))

    control_image = cv2.copyMakeBorder(control_image, top=0, bottom=0, left=int((width-control_image.shape[1])/2), right=int((width-control_image.shape[1])/2), borderType=cv2.BORDER_CONSTANT, value=(0,255,0))

    # Comparar os pixels e contar os iguais 
    
    same_pixels = np.sum(control_image == image) // 3  

    total_pixels = height * width

    # Calcular a percentagem de pixeis iguais
    score = same_pixels/total_pixels*100

    return(score)