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

    # Variáveis para as formas
    pressing_s = False
    pressing_o = False
    pressing_e = False
    engaged = False
    let_go_sum = 0

    # Abrir o desenho para colorir
    if coloringimage:
        img = load_image(height, width, "./img/flor.jpeg")
        cv2.imshow("Imagem para colorir", cv2.subtract(np.ones((height, width, 3)) * 255, img, dtype=cv2.CV_64F))

        print(Style.BRIGHT + "\nCores para pintar a imagem:" + Style.RESET_ALL)
        print(Fore.GREEN + "\tVerde: " + Style.RESET_ALL + "1")
        print(Fore.RED + "\tVermelho: " + Style.RESET_ALL + "2")
        print(Fore.BLUE + "\tAzul: " + Style.RESET_ALL + "3\n")


    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        originalframe = frame.copy()

        pressing = pressing_e | pressing_o | pressing_s
        
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
                
                # Ver se esta a ser desenhada alguma forma (quadrado ou circulo) ou não
                if not pressing:
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

                else:
                    # Criar uma tela de desenho temporaria para desenhar os varios tamanhos da forma
                    temp_canvas = canvas.copy()
                    if pressing_s:
                        cv2.rectangle(temp_canvas, figure_initial, centroid, pencil_color, pencil_thickness)
                    elif pressing_o:
                        radius = round(math.sqrt(abs((figure_initial[0]-centroid[0])**2+(figure_initial[1]-centroid[1])**2)))
                        cv2.circle(temp_canvas,figure_initial,radius,pencil_color,pencil_thickness)

                # Atualizar a última posição
                last_centroid = centroid
        
        # Definir qual vai ser a tela de desenho a morstrar
        if pressing:
            # Caso se esteja a criar uma forma será a tela de desenho temporaria
            show_canvas = temp_canvas.copy()
        else:
            # Caso contrario será a normal
            show_canvas = canvas.copy()

        if videocanva:
            # Caso se esteja a usar o VideoCanvas a tela de desenho será uma variante da anterior
            show_canvas = video_canvas(show_canvas, originalframe)

        # Mostra a tela de desenho e a captura de vídeo na mesma janela
        cv2.imshow("Canvas and Camera", np.concatenate([cv2.flip(show_canvas,1),cv2.flip(frame,1)], axis=1))

        k = cv2.waitKey(1)


        
        # Chama a função que toma conta das formas
        if pressing:
            pressing_s, pressing_o, engaged, let_go_sum, canvas = handle_shapes(k, pressing_s, pressing_o, engaged, let_go_sum, canvas, temp_canvas)

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
        elif (k == ord("s") or k == ord("S")) and not pressing and largest_contour is not None:
            pressing_s = True
            figure_initial = centroid
        elif (k == ord("o") or k == ord("O")) and not pressing and largest_contour is not None:
            pressing_o = True
            figure_initial = centroid
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