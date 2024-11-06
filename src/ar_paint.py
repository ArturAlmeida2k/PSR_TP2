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
global path, shake, videocanva, coloringimage, evaluation


#  ------------------------------
#  -----     Functions      -----
#  ------------------------------
def main():
    # Abrir o ficheiro limits.json em modo leitura
    with open(path,"r") as json_file:
        limits = json.load(json_file)["limits"]

    # Iniciar captura de vídeo
    cap = start_video_capture()
    cap.set(3,640)
    cap.set(4,480)
    ret, frame = cap.read()

    # Definir as dimensões para a area de pintura baseado nas dimensão do video
    height, width, _ = frame.shape
    print(height, " ",width)
    if coloringimage:
        # Carregar e apresentar a imagem a colorir se requisitado
        print(Style.BRIGHT + "\nCores para pintar a imagem:" + Style.RESET_ALL)
        print(Fore.GREEN + "\tVerde: " + Style.RESET_ALL + "1")
        print(Fore.RED + "\tVermelho: " + Style.RESET_ALL + "2")
        print(Fore.BLUE + "\tAzul: " + Style.RESET_ALL + "3\n")
        canvas = cv2.flip(blank_coloring_image(height, width, "./img/flor.jpeg"), 1)
    else:
        canvas = create_blank_canvas(width, height)

    # Variáveis para o lápis
    last_centroid = None  # Ponto anterior (para desenhar linhas)
    pencil_color = (0, 0, 255)  # Cor do lápis a vermelho
    pencil_thickness = 5  # Espessura da linha

    # Variáveis para as formas
    pressing_s = False
    pressing_o = False
    engaged = False
    let_go_sum = 0
    
    
    # Ciclo para captura de frames e pintura
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        hsv_frame = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)

        originalframe = frame.copy()
        pressing = pressing_o | pressing_s

        # Criação de uma mascara baseado em limites de canais de cor
        mask = cv2.inRange(hsv_frame,
                           (limits["H"]["min"], limits["S"]["min"], limits["V"]["min"]),
                           (limits["H"]["max"], limits["S"]["max"], limits["V"]["max"]))

        # Interação com a câmara
        largest_contour = get_largest_contour(mask)
        if largest_contour is not None:
            # Destacar o objeto de maior área pintando-o de verde
            cv2.drawContours(frame, [largest_contour], -1, (0, 255, 0), 2)
            
            # Calcular o centroide do objeto
            centroid = get_centroid(largest_contour)
            if centroid is not None:
                # Desenhar uma cruz vermelha no centroide
                cv2.drawMarker(frame, centroid, (0, 0, 255), markerType=cv2.MARKER_CROSS, markerSize=20, thickness=2)
                
                # Ver se está a ser desenhada alguma forma (quadrado ou circulo)
                if not pressing:
                    # Usar o centroide para desenhar na tela
                    if not shake and last_centroid is not None:
                        # Desenhar uma linha da última posição para a nova
                        cv2.line(canvas, last_centroid, centroid, pencil_color, pencil_thickness)

                    elif shake and last_centroid is not None:
                        # Calcular a distância entre o centro atual e o anterior e definir a distância máxima.
                        distance = math.sqrt(abs((last_centroid[0]-centroid[0])**2+(last_centroid[1]-centroid[1])**2))
                        maximum_distance = 75

                        if distance <= maximum_distance:
                            # Desenhar uma linha da última posição para a nova
                            cv2.line(canvas, last_centroid, centroid, pencil_color, pencil_thickness)
                        else:
                            # Desenhar um ponto no centro atual
                            cv2.line(canvas, centroid, centroid, pencil_color, pencil_thickness)

                else:
                    # Criar uma tela de desenho temporária para desenhar os vários tamanhos da forma
                    temp_canvas = canvas.copy()
                    if pressing_s:
                        cv2.rectangle(temp_canvas, figure_initial, centroid, pencil_color, pencil_thickness)
                    elif pressing_o:
                        radius = round(math.sqrt(abs((figure_initial[0]-centroid[0])**2+(figure_initial[1]-centroid[1])**2)))
                        cv2.circle(temp_canvas,figure_initial,radius,pencil_color,pencil_thickness)

                # Atualizar a última posição
                last_centroid = centroid

        # Definir qual vai ser a tela de desenho a mostrar
        if pressing:
            # Caso se esteja a criar uma forma será a tela de desenho temporária
            show_canvas = temp_canvas.copy()
        else:
            # Caso contrario será a normal
            show_canvas = canvas.copy()


        
        # Mostrar janelas conforme as configurações iniciais
        if not videocanva and not coloringimage:
            cv2.imshow("Tela Branca", np.concatenate([cv2.flip(frame, 1), cv2.flip(show_canvas, 1)], axis=1))
        elif videocanva and not coloringimage:
            show_canvas = video_canvas(show_canvas, originalframe)
            cv2.imshow("Tela Branca", np.concatenate([cv2.flip(frame, 1), cv2.flip(show_canvas, 1)], axis=1))
        elif coloringimage and not videocanva:
            cv2.imshow("Imagem para colorir", np.concatenate([cv2.flip(frame, 1), cv2.flip(show_canvas, 1)], axis=1))
        elif videocanva and coloringimage:
            show_canvas = video_canvas(show_canvas, originalframe)
            cv2.imshow("Tela e Imagem", np.concatenate([cv2.flip(frame, 1), cv2.flip(show_canvas, 1)], axis=1))

        
        k = cv2.waitKey(1)

        # Chama a função que toma conta das formas
        if pressing:
            pressing_s, pressing_o, engaged, let_go_sum, canvas = handle_shapes(k, pressing_s, pressing_o, engaged, let_go_sum, canvas, temp_canvas)


        
        # Teclas de controle de cor, grossura de pincel, limpeza de tela e guardar imagem
        if k == ord("r") or k == ord("R"):
            pencil_color = (0, 0, 255)
            print("Lápis", Fore.RED + "vermelho" + Style.RESET_ALL)

        elif k == ord("g") or k == ord("G"):
            pencil_color = (0, 255, 0)
            print("Lápis", Fore.GREEN + "verde" + Style.RESET_ALL)

        elif k == ord("b") or k == ord("B"):
            pencil_color = (255, 0, 0)
            print("Lápis", Fore.BLUE + "azul" + Style.RESET_ALL)

        elif k == ord("+"):
            pencil_thickness = min(pencil_thickness + 1, 25)
            print("Tamanho do lápis:", pencil_thickness)

        elif k == ord("-"):
            pencil_thickness = max(pencil_thickness - 1, 1)
            print("Tamanho do lápis:", pencil_thickness)

        elif k == ord("c") or k == ord("C"):
            if coloringimage:
                canvas = cv2.flip(blank_coloring_image(height, width, "./img/flor.jpeg"), 1)
            else:
                canvas.fill(255)
            print("Tela limpa")

        elif k == ord("w") or k == ord("W"):
            now = datetime.now()
            formatted_time = now.strftime("drawing_%a_%b_%d_%H:%M:%S_%Y.png")
            # Salvar a imagem da tela com o nome formatado
            cv2.imwrite(formatted_time, cv2.flip(canvas, 1))
            print(f"Imagem salva como {formatted_time}")
            # Fazer a avaliação
            if evaluation:
                score = evaluate_painting("./drawing_Sun_Nov_03_20:54:29_2024.png") # PARA TESTAR DEPOIS POR "formatted_time"
                print(f"Precisão da pintura: {score:.2f}%")

        elif (k == ord("s") or k == ord("S")) and not pressing and largest_contour is not None:
            pressing_s = True
            figure_initial = centroid

        elif (k == ord("o") or k == ord("O")) and not pressing and largest_contour is not None:
            pressing_o = True
            figure_initial = centroid

        elif k == ord("q") or k == ord("Q"):
            cap.release()
            cv2.destroyAllWindows()
            print("Fim")
            break



#  ------------------------------
#  -----    Startup Code    -----
#  ------------------------------
if __name__ == '__main__':

    # Ir buscar todos os argumentos
    path, shake, videocanva, coloringimage, evaluation = parseArguments()
    
    main()
