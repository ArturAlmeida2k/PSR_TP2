#!/usr/bin/env python3


#  ------------------------------
#  -----      Imports       -----
#  ------------------------------
import cv2
import json
import math
import numpy as np
from utils.argumentParser import parseArguments
from utils.functions import *
from datetime import datetime


#  ------------------------------
#  -----     Variables      -----
#  ------------------------------
global path, shake


#  ------------------------------
#  -----     Functions      -----
#  ------------------------------
def main():
    global path, shake
    
    # Abrir o ficheiro limits.json em modo leitura
    with open(path,"r") as json_file:
        limits = json.load(json_file)["limits"]

    # Iniciar a captura da câmara
    cap = start_video_capture()

    ret, frame = cap.read()
    
    height, width, _ = frame.shape
    canvas = create_blank_canvas(width, height)
    
    
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
                if (last_centroid is not None and not shake) or (last_centroid is not None and math.sqrt(abs((last_centroid[0]-centroid[0])**2+(last_centroid[1]-centroid[1])**2)) < 50 and shake):
                    
                    # Desenhar uma linha da última posição para a nova
                    cv2.line(canvas, last_centroid, centroid, pencil_color, pencil_thickness)
                
                # Atualizar a última posição
                last_centroid = centroid
        

        # Mostra a tela de desenho (por enquanto vazia) e a captura de vídeo
        #cv2.imshow("Canvas", canvas)
        #cv2.imshow("Camera", frame)
        cv2.imshow("Canvas and Camera", np.hstack((cv2.resize(cv2.flip(canvas, 1), (640, 540)), cv2.resize(cv2.flip(frame, 1), (640, 540)))))

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
            canvas.fill(255)
        elif k == ord("w"):
            now = datetime.now()
            formatted_time = now.strftime("drawing_%a_%b_%d_%H:%M:%S_%Y.png")
            
            # Salvar a imagem da tela com o nome formatado
            cv2.imwrite(formatted_time, canvas)
            print(f"Imagem salva como {formatted_time}")
        elif k == ord("q"):
            cap.release()
            cv2.destroyAllWindows()
            break
   


#  ------------------------------
#  -----    Startup Code    -----
#  ------------------------------
if __name__ == '__main__':

    #  Retrieve all the arguments
    path, shake = parseArguments()

    #  Call the main code
    main()


