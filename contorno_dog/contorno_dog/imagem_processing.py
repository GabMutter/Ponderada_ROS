import cv2
import numpy as np

def extrair_caminho(caminho_arquivo):
    print("Iniciando processamento de imagem...")
    
    # 1. Carregamento da imagem
    img_bgr = cv2.imread(caminho_arquivo)
    
    # Converte BGR para RGB
    img_rgb = img_bgr[:,:,::-1]  
    
    # 2. Escala de Cinza
    R, G, B = img_rgb[:,:,0], img_rgb[:,:,1], img_rgb[:,:,2]
    img_cinza = (0.299 * R + 0.587 * G + 0.114 * B).astype(np.float64)
    
    # 3. Convolução e Blur
    def aplicar_convolucao(imagem, kernel):
        alt, larg = imagem.shape
        k_alt, k_larg = kernel.shape
        pad_h, pad_w = k_alt // 2, k_larg // 2
        img_padded = np.pad(imagem, ((pad_h, pad_h), (pad_w, pad_w)), mode='edge')
        img_saida = np.zeros_like(imagem)
        for y in range(alt):
            for x in range(larg):
                regiao = img_padded[y:y+k_alt, x:x+k_larg]
                img_saida[y, x] = np.sum(regiao * kernel)
        return img_saida

    kernel_gaussiano = np.array([
        [1, 4, 7, 4, 1],
        [4, 16, 26, 16, 4],
        [7, 26, 41, 26, 7],
        [4, 16, 26, 16, 4],
        [1, 4, 7, 4, 1]
    ]) / 273.0
    img_suavizada = aplicar_convolucao(img_cinza, kernel_gaussiano)
    
    # 4. Filtro de Sobel (Detecção de Bordas)
    sobel_x = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]])
    sobel_y = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]])
    grad_x = aplicar_convolucao(img_suavizada, sobel_x)
    grad_y = aplicar_convolucao(img_suavizada, sobel_y)
    magnitude = np.sqrt(grad_x**2 + grad_y**2)
    magnitude = (magnitude / np.max(magnitude) * 255).astype(np.uint8)
    
    # Threshold
    bordas = np.where(magnitude > 60, 255, 0).astype(np.uint8)
    
    # 5. Mapeamento para o Turtlesim
    linhas_y, colunas_x = np.where(bordas == 255)
    alt_img, larg_img = bordas.shape
    linhas_y = alt_img - linhas_y
    fator_escala = 11.0 / max(alt_img, larg_img)
    turtlesim_x = colunas_x * fator_escala
    turtlesim_y = linhas_y * fator_escala
    
    coordenadas_totais = list(zip(turtlesim_x, turtlesim_y))
    passo = 3
    caminho_final = coordenadas_totais[::passo]
    
    print(f"Processamento concluído. {len(caminho_final)} pontos extraídos.")
    return caminho_final