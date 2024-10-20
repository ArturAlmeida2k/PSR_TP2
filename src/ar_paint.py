#!/usr/bin/env python3


import cv2
import json
import numpy as np
from utils.argumentParser import parseArguments

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


def main():
    global path
    print(path)
    with open(path,"r") as json_file:
        limits = json.load(json_file)
    
    cap = setup_video_capture()

    ret, frame = cap.read()
    if ret:
        height, width, _ = frame.shape
        canvas = create_blank_canvas(width, height)
    else:
        print("Erro ao capturar a primeira imagem da câmara.")
        cap.release()
        return
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Mostra a tela de desenho (por enquanto vazia) e a captura de vídeo
        cv2.imshow('Canvas', canvas)
        cv2.imshow('Camera', frame)

        # Teclas de controle
        if cv2.waitKey(1) == ord('q'):
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


