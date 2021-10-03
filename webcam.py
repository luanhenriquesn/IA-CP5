#!/usr/bin/python
# -*- coding: utf-8 -*-


import cv2
import os,sys, os.path
import numpy as np
import math
import time
#Classe construida para fazer direct inputs e conseguirmos refletir o pressionamento de teclas nos jogos. 
#Este código foi utilizado em um vídeo gringo: https://www.youtube.com/watch?v=tWqbl9IUdCg  - Com base em um código do stackoverflow.
#Para mais detalhes, basta abrir o arquivo directkeys.py 
from directkeys import PressKey, ReleaseKey, W, A, S, D


#filtro vermelho parte baixa
image_lower_hsv1 = np.array([170,150,150])
image_upper_hsv1 = np.array([180,255,255])

#filtro vermelho parte alta
image_lower_hsv2 = np.array([0,130,130])
image_upper_hsv2 = np.array([7,255,255])

#filtro verde agua
image_lower_hsv3 = np.array([82,127,127])
image_upper_hsv3 = np.array([93,255,255])


def filtro_de_cor(img_bgr, low_hsv, high_hsv):
    """ retorna a imagem filtrada"""
    img = cv2.cvtColor(img_bgr,cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(img, low_hsv, high_hsv)
    return mask 

def mascara_or(mask1, mask2):

    """ retorna a mascara or"""
    mask = cv2.bitwise_or(mask1, mask2)
    return mask

def desenha_cruz(img, cX,cY, size, color):
     """ faz a cruz no ponto cx cy"""
     cv2.line(img,(cX - size,cY),(cX + size,cY),color,5)
     cv2.line(img,(cX,cY - size),(cX, cY + size),color,5)    

def escreve_texto(img, text, origem, color):
     """ escreve um texto no local desejado"""
 
     font = cv2.FONT_HERSHEY_SIMPLEX
     cv2.putText(img, str(text), origem, font,1,color,2,cv2.LINE_AA)

def image_da_webcam(img):
    """
    ->>> !!!! FECHE A JANELA COM A TECLA ESC !!!! <<<<-
        deve receber a imagem da camera e retornar uma imagems filtrada.
    """  

    #Obtendo as máscaras dos dois tons de vermelho, e do tom de verde.
    mask_hsv1 = filtro_de_cor(img, image_lower_hsv1, image_upper_hsv1)
    mask_hsv2 = filtro_de_cor(img, image_lower_hsv2, image_upper_hsv2)
    mask_hsv3 = filtro_de_cor(img, image_lower_hsv3, image_upper_hsv3)

    #Juntando as imagens vermelhas
    mask_hsv = mascara_or(mask_hsv1, mask_hsv2)
    #Juntando a imagem vermelha com a verde.
    mask_hsv = mascara_or(mask_hsv, mask_hsv3)

    #Obtendo o contorno de todos os circulos
    contornos, _ = cv2.findContours(mask_hsv, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE) 

    mask_rgb = cv2.cvtColor(mask_hsv, cv2.COLOR_GRAY2RGB) 
    contornos_img = mask_rgb.copy()
    
    #Descobrindo os dois maiores contornos
    maior = None
    maior_area = 0
    segundo_maior = None
    segunda_maior_area = 0
    for c in contornos:
        area = cv2.contourArea(c)
        if area > maior_area:
            segunda_maior_area = maior_area
            maior_area = area
            segundo_maior = maior
            maior = c
        elif area > segunda_maior_area:
            segunda_maior_area = area
            segundo_maior = c
    
    #Obtendo o centro de massa dos dois maiores contornos
    M1 = cv2.moments(maior)
    M2 = cv2.moments(segundo_maior)

    # Verificando se o centro de massa dos dois contornos foram obtidos com sucesso
    if M1["m00"] != 0 and M2["m00"] != 0:

        #Obtendo as cordenadas x e y dos dois centro de massa
        cX1 = int(M1["m10"] / M1["m00"])
        cY1 = int(M1["m01"] / M1["m00"])
        cX2 = int(M2["m10"] / M2["m00"])
        cY2 = int(M2["m01"] / M2["m00"])
        
        cv2.drawContours(contornos_img, [maior], -1, [255, 0, 0], 5)
        cv2.drawContours(contornos_img, [segundo_maior], -1, [255, 0, 0], 5)
       
        #faz as cruzes nos centros de massa
        desenha_cruz(contornos_img, cX1,cY1, 20, (0,0,255))
        desenha_cruz(contornos_img, cX2,cY2, 20, (0,0,255))

        #Escrevendo os valores dos centros de massa, e as areas
        texto1 = f"Circulo 1: {cY1}y{cX1}x - Area: {maior_area}"
        escreve_texto(contornos_img, texto1, (0,30), (0,255,0))

        texto2 = f"Circulo 2: {cY2}y{cX2}x - Area: {segunda_maior_area}" 
        escreve_texto(contornos_img, texto2, (0,70), (0,255,0)) 

        #Traçando a reta entre os dois centros dos círculos
        cv2.line(contornos_img,(cX1, cY1),(cX2, cY2), (0,0,255), 5)

        #Calculando o radiano
        rad = math.atan2(cY1 - cY2, cX1 - cX2)
        #Passando pra angulo em graus e arredondando
        ang = round( math.degrees(rad) )

        #Escrevendo o valor do angulo na tela.
        texto3 = f"Angulo: {ang}" 
        escreve_texto(contornos_img, texto3, (0,110), (0,255,0)) 

        #De acordo com a proximidade do celular da camera, movimentar o personagem para frente(W) ou para trás(S).
        if maior_area > 5000 :
            escreve_texto(contornos_img, "Tecla W - Andar pra frente", (0,150), (0,255,0))
            PressKey(W)
            time.sleep(0.09)
            ReleaseKey(W)
        elif maior_area < 3000 and maior_area != 0:
            escreve_texto(contornos_img, "Tecla S - Andar pra tras", (0,150), (0,255,0))
            PressKey(S)
            time.sleep(0.09)
            ReleaseKey(S)

        #De acordo com a inclinação do celular levemente para a esquerda ou para a direita, movimentar o personagem para esquerda (A) ou para a direita (D).
        if ang > 36:
            escreve_texto(contornos_img, "Tecla A - Virar pra esquerda", (0,190), (0,255,0))
            PressKey(A)
            time.sleep(0.09)
            ReleaseKey(A) 
        elif ang < 20:
            escreve_texto(contornos_img, "Tecla D - Virar pra direita", (0,190), (0,255,0))
            PressKey(D)
            time.sleep(0.09)
            ReleaseKey(D)
            
    else:
    # se não existe nada para segmentar 
        texto = 'nao tem nada'
        escreve_texto(contornos_img, texto, (0,30), (0,0,255))
    


    return contornos_img

cv2.namedWindow("preview")
# define a entrada de video para webcam
vc = cv2.VideoCapture(0)

#configura o tamanho da janela 
vc.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
vc.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

if vc.isOpened(): # try to get the first frame
    rval, frame = vc.read()
else:
    rval = False

while rval:
    
    img = image_da_webcam(frame) # passa o frame para a função imagem_da_webcam e recebe em img imagem tratada

    cv2.imshow("preview", img)
    cv2.imshow("original", frame)
    rval, frame = vc.read()
    key = cv2.waitKey(20)
    if key == 27: # exit on ESC
        break

cv2.destroyWindow("preview")
vc.release()
