#!/usr/bin/env python3


import cv2
import json
import numpy as np
from utils.argumentParser import parseArguments
from datetime import datetime

global path

def setup_video_capture():
    # Iniciar a captura de vídeo
    cap = cv2.VideoCapture(0)  # '0' indica a webcam padrão. Altere se necessário.
    
    # Verificar se a câmera foi inicializada corretamente
    if not cap.isOpened():
        print("Erro: Não foi possível abrir a câmara.")
        exit()

    # Opcional: Definir a resolução do vídeo (pode ajustar conforme necessário)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    return cap


def create_blank_canvas(width, height):
    # Criar uma imagem branca com as mesmas dimensões da captura de vídeo
    canvas = 255 * np.ones(shape=[height, width, 3], dtype=np.uint8)  # Imagem RGB branca
    return canvas

def get_largest_contour(mask):
    # Encontrar todos os contornos na máscara
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Se nenhum contorno for encontrado
    if len(contours) == 0:
        return None
    
    # Encontrar o maior contorno
    largest_contour = max(contours, key=cv2.contourArea)
    
    return largest_contour

def get_centroid(contour):
    M = cv2.moments(contour)
    
    if M["m00"] == 0:  # Evitar divisão por zero
        return None
    
    # Cálculo das coordenadas do centróide
    cx = int(M["m10"] / M["m00"])
    cy = int(M["m01"] / M["m00"])
    
    return (cx, cy)

def main():
    global path
    
    with open(path,"r") as json_file:
        limits = json.load(json_file)["limits"]
    
    #limits = limits["limits"]

    cap = setup_video_capture()

    ret, frame = cap.read()
    if ret:
        height, width, _ = frame.shape
        canvas = create_blank_canvas(width, height)
    else:
        print("Erro ao capturar a primeira imagem da câmara.")
        cap.release()
        return
    
     # Variáveis para o lápis
    last_centroid = None  # Ponto anterior (para desenhar linhas)
    pencil_color = (0, 0, 255)  # Cor do lápis (vermelho)
    pencil_thickness = 5  # Espessura da linha


    while True:
        ret, frame = cap.read()
        if not ret:
            break
    
        mask = cv2.inRange(frame,(limits["B"]["min"],limits["G"]["min"],limits["R"]["min"]),(limits["B"]["max"],limits["G"]["max"],limits["R"]["max"]))       

        largest_contour = get_largest_contour(mask)
        if largest_contour is not None:
            # Destacar o objeto de maior área pintando-o de verde
            cv2.drawContours(frame, [largest_contour], -1, (0, 255, 0), 2)
            
            # 4. Calcular o centróide do objeto
            centroid = get_centroid(largest_contour)
            if centroid is not None:
                # Desenhar uma cruz vermelha no centróide
                cv2.drawMarker(frame, centroid, (0, 0, 255), markerType=cv2.MARKER_CROSS, 
                               markerSize=20, thickness=2)
                
                # 5. Usar o centroide para desenhar na tela (canvas)
                if last_centroid is not None:
                    # Desenhar uma linha da última posição para a nova
                    cv2.line(canvas, last_centroid, centroid, pencil_color, pencil_thickness)
                
                # Atualizar a última posição
                last_centroid = centroid
        

        # Mostra a tela de desenho (por enquanto vazia) e a captura de vídeo
        cv2.imshow("Canvas", canvas)
        cv2.imshow("Camera", frame)

        k = cv2.waitKey(1)
        # Teclas de controle
        
        if k == ord("r"):
            pencil_color = (0,0,255)
        elif k == ord("g"):
            pencil_color = (0,255,0)
        elif k == ord("b"):
            pencil_color = (255,0,0)
        elif k == ord("+"):
            pencil_thickness += 1
        elif k == ord("-"):
            pencil_thickness = max(pencil_thickness - 1,1)
        elif k == ord("c"):
            canvas = create_blank_canvas(width, height)
        elif k == ord("w"):
            now = datetime.now()
            formatted_time = now.strftime("drawing_%a_%b_%d_%H:%M:%S_%Y.png")
            
            # Salvar a imagem (tela) com o nome formatado
            cv2.imwrite(formatted_time, canvas)
            print(f"Imagem salva como {formatted_time}")
        elif k == ord("q"):
            break


    # Liberar a captura e fechar as janelas
    cap.release()
    cv2.destroyAllWindows()



#  ------------------------------
#  -----    Startup Code    -----
#  ------------------------------
if __name__ == '__main__':

    #  Retrieve all the arguments
    path = parseArguments()

    #  Call the main code
    main()


