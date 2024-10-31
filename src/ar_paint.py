#!/usr/bin/env python3


#  ------------------------------
#  -----      Imports       -----
#  ------------------------------
import cv2
import json
import math
import numpy as np
from colorama import Style, Fore
from utils.argumentParser import parseArguments
from utils.functions import *
from datetime import datetime



#  ------------------------------
#  -----     Variables      -----
#  ------------------------------
global path, shake, videocanva


#  ------------------------------
#  -----     Functions      -----
#  ------------------------------
def main():
    global path, shake
    
    # Abrir o ficheiro limits.json em modo leitura
    with open(path,"r") as json_file:
        limits = json.load(json_file)["limits"]

    # Iniciar captura de vídeo
    cap = start_video_capture()

    ret, frame = cap.read()
    
    height, width, _ = frame.shape
    canvas = create_blank_canvas(width, height)
    
    
    # Variáveis para o lápis
    last_centroid = None  # Ponto anterior (para desenhar linhas)
    pencil_color = (0, 0, 255)  # Cor do lápis a vermelho
    pencil_thickness = 5  # Espessura da linha

    pressing_s = False

    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        originalframe = frame.copy()

        mask = cv2.inRange(frame,(limits["B"]["min"],limits["G"]["min"],limits["R"]["min"]),(limits["B"]["max"],limits["G"]["max"],limits["R"]["max"]))       

        largest_contour = get_largest_contour(mask)
        if largest_contour is not None:
            # Destacar o objeto de maior área pintando-o de verde
            cv2.drawContours(frame, [largest_contour], -1, (0, 255, 0), 2)
            
            # Calcular o centróide do objeto
            centroid = get_centroid(largest_contour)
            if centroid is not None:
                # Desenhar uma cruz vermelha no centróide
                cv2.drawMarker(frame, centroid, (0, 0, 255), markerType=cv2.MARKER_CROSS, 
                               markerSize=20, thickness=2)
                
                # Usar o centroide para desenhar na tela
                if not shake and last_centroid is not None:
                    
                    # Desenhar uma linha da última posição para a nova
                    cv2.line(canvas, last_centroid, centroid, pencil_color, pencil_thickness)

                elif shake and last_centroid is not None:
                    # Calcular a distancia entre o centro atual e o anterior e definir a distancia maxima.
                    distance = math.sqrt(abs((last_centroid[0]-centroid[0])**2+(last_centroid[1]-centroid[1])**2))
                    maximum_distance = 75

                    if distance <= maximum_distance: 
                        # Desenhar uma linha da última posição para a nova
                          cv2.line(canvas, last_centroid, centroid, pencil_color, pencil_thickness)
                    else:
                        # Desenhar um ponto no centro atual
                        cv2.line(canvas, centroid, centroid, pencil_color, pencil_thickness)

                # Atualizar a última posição
                last_centroid = centroid
        

        # Mostra a tela e a captura de vídeo sobrepostas
        if videocanva:

            canvas_frame = video_canvas(canvas, originalframe)
            # Tornar o background do canvas preto para poder fazer cv2.add() 
            canvas[np.all(canvas == [255, 255, 255], axis=-1)] = [0, 0, 0]
            
            # Armazenar onde exitem a cor vermelha|verde|azul para quando se juntar a frame não somar valores aos 0's
            red_mask = np.all(canvas == [0, 0, 255], axis=-1)
            green_mask = np.all(canvas == [0, 255, 0], axis=-1)
            blue_mask = np.all(canvas == [255, 0, 0], axis=-1)
            color_mask = red_mask | green_mask | blue_mask
            
            canvas_frame = np.where(color_mask[..., None], canvas, cv2.add(originalframe, canvas))

            # Mostra a tela de desenho com a frame como background e a captura de vídeo na mesma janela
            cv2.imshow("Canvas and Camera", np.concatenate([cv2.flip(canvas_frame,1),cv2.flip(frame,1)], axis=1))

        else:
            # Mostra a tela de desenho vazia e a captura de vídeo na mesma janela
            cv2.imshow("Canvas and Camera", np.concatenate([cv2.flip(canvas,1),cv2.flip(frame,1)], axis=1))

        k = cv2.waitKey(1)

        # Obter o objeto
        image_grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(image_grey, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(thresh, 4, cv2.CV_32S)

        if coloringimage:
            image, labelColors, labelMatrix = load_image(height, width)
            cv2.imshow("Imagem para colorir", cv2.subtract(np.ones((height, width, 3)) * 255, image, dtype=cv2.CV_64F))
            
            redline=""
            greenline=""
            blueline=""
            for i in range(len(labelColors)):
                if labelColors[i] == (0,0,255):
                    redline += str(i) + ", "
                elif labelColors[i] == (0,255,0):
                    greenline += str(i) + ", "
                elif labelColors[i] == (255,0,0):
                    blueline+= str(i) + ", "
            print(Style.BRIGHT + "Cores para pintar a imagem:" + Style.RESET_ALL)
            print(Fore.RED + "Vermelho: " + Style.RESET_ALL + redline[:-2])
            print(Fore.GREEN + "Verde: " + Style.RESET_ALL + greenline[:-2])
            print(Fore.BLUE + "Azul: " + Style.RESET_ALL + blueline[:-2])

        if num_labels > 1:
            # Obter o centro do espaço de maior área
            max_area_label = sorted([(i, stats[i, cv2.CC_STAT_AREA]) for i in range(num_labels)], key=lambda x: x[1])[-2][0]
            maskci = cv2.inRange(labels, max_area_label, max_area_label)
            maskci = maskci.astype(bool)
            frame[maskci] = (0, 255, 0)


        if pressing_s and (k != ord("s") or k != ord("S")):
            print(k)
            print("here")
            pressing_s = False

        # Teclas de controle
        if k == ord("r") or k == ord("R"):
            pencil_color = (0,0,255)
            print("Lápis", Fore.RED + "vermelho" + Style.RESET_ALL)
        elif k == ord("g") or k == ord("G"):
            pencil_color = (0,255,0)
            print("Lápis", Fore.GREEN + "verde" + Style.RESET_ALL)
        elif k == ord("b") or k == ord("B"):
            pencil_color = (255,0,0)
            print("Lápis", Fore.BLUE + "azul" + Style.RESET_ALL)
        elif k == ord("+"):
            pencil_thickness += 1
            print("Tamanho do lápis:", pencil_thickness)
        elif k == ord("-"):
            pencil_thickness = max(pencil_thickness - 1,1)
            print("Tamanho do lápis:", pencil_thickness)
        elif k == ord("c") or k == ord("C"):
            canvas.fill(255)
            print("Tela limpa")
        elif k == ord("w") or k == ord("W"):
            now = datetime.now()
            formatted_time = now.strftime("drawing_%a_%b_%d_%H:%M:%S_%Y.png")
            # Salvar a imagem da tela com o nome formatado
            cv2.imwrite(formatted_time, cv2.flip(canvas, 1))
            print(f"Imagem salva como {formatted_time}")
        elif k == ord("s") or k == ord("S"):
            pressing_s = True
            print("here here")
        elif k == ord("o") or k == ord("O"):
            pass
        elif k == ord("e") or k == ord("E"):
            pass
        elif k == ord("q") or k == ord("Q"):
            cap.release()
            cv2.destroyAllWindows()
            break
   


#  ------------------------------
#  -----    Startup Code    -----
#  ------------------------------
if __name__ == '__main__':

    # Ir buscar todos os argumentos
    path, shake, videocanva, coloringimage = parseArguments()
    
    main()