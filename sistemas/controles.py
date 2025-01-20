import pygame
import random
import math

from config.configuracoes import LARGURA, ALTURA

class ControleAviao:
    # Constantes
    DISTANCIA_FUGA = 0.3      # 30% - Muito perto, precisa fugir
    DISTANCIA_MINIMA = 0.4    # 40% - Distância mínima para tiro
    DISTANCIA_IDEAL = 0.6     # 60% - Distância boa para combate
    DISTANCIA_TIRO = 0.8      # 80% - Máxima distância para tiro
    DISTANCIA_PAREDE = 0   # 15% - Distância mínima da parede

    @staticmethod
    def controlar_jogador(aviao, teclas):
        if teclas[pygame.K_LEFT]:
            aviao.angulo += 5
        if teclas[pygame.K_RIGHT]:
            aviao.angulo -= 5
        if teclas[pygame.K_UP]:
            aviao.velocidade = min(aviao.velocidade + aviao.aceleracao, aviao.velocidade_max)
        if teclas[pygame.K_DOWN]:
            aviao.velocidade = max(0.3, aviao.velocidade - aviao.aceleracao)
        if teclas[pygame.K_SPACE]:
            aviao.atirar()

    @staticmethod
    def avaliar_situacao(sensores_parede, sensores_aviao):
        sensor_parede_proximo = min(sensores_parede)
        indice_parede_proximo = sensores_parede.index(sensor_parede_proximo)
        
        # Encontra o avião mais próximo
        indice_aviao = -1
        dist_aviao = float('inf')
        alvo_alinhado = False
        
        for i, valor in enumerate(sensores_aviao):
            if valor > 0 and valor < dist_aviao:
                dist_aviao = valor
                indice_aviao = i
                alvo_alinhado = i in [0, 1, 7]  # Sensores frontais
                
        em_perigo = (sensor_parede_proximo < ControleAviao.DISTANCIA_PAREDE or 
                    (indice_aviao != -1 and dist_aviao < ControleAviao.DISTANCIA_FUGA))
                    
        return sensor_parede_proximo, indice_parede_proximo, indice_aviao, dist_aviao, alvo_alinhado, em_perigo

    @staticmethod
    def calcular_direcao_fuga(aviao):
        centro_x = LARGURA / 2
        centro_y = ALTURA / 2
        
        dx = centro_x - aviao.x
        dy = centro_y - aviao.y
        
        # Ajustado para permitir maior aproximação das bordas
        if (aviao.x < LARGURA * 0.1 or aviao.x > LARGURA * 0.9 or 
            aviao.y < ALTURA * 0.1 or aviao.y > ALTURA * 0.9):
            angulo_centro = math.degrees(math.atan2(-dy, dx))
            return angulo_centro + random.uniform(-30, 30)
            
        return -1

    @staticmethod
    def modo_fuga(aviao, sensor_parede_proximo, indice_parede_proximo, indice_aviao):
        if sensor_parede_proximo < ControleAviao.DISTANCIA_PAREDE or aviao.colidindo:
            # Reduz menos a velocidade
            aviao.velocidade = aviao.velocidade_max * (0.4 if aviao.colidindo else 0.6)
            
            if aviao.colidindo:
                direcao_fuga = ControleAviao.calcular_direcao_fuga(aviao)
                aviao.angulo = direcao_fuga
                return

            direcao_fuga = ControleAviao.calcular_direcao_fuga(aviao)
            if direcao_fuga == -1:
                direcao_fuga = (indice_parede_proximo * 45 + 180 + random.uniform(-30, 30)) % 360
            
            taxa_curva = 0.5
        else:
            aviao.velocidade = aviao.velocidade_max * 0.9  # Aumentada velocidade normal
            direcao_fuga = (indice_aviao * 45 + 180) % 360
            taxa_curva = 0.3
            
        diff_angulo = (direcao_fuga - aviao.angulo + 180) % 360 - 180
        aviao.angulo += diff_angulo * taxa_curva

    @staticmethod
    def modo_combate(aviao, dist_aviao, indice_aviao):
        if dist_aviao < ControleAviao.DISTANCIA_MINIMA:
            # Mantém distância com velocidade moderada
            aviao.velocidade = aviao.velocidade_max * 0.6
            direcao_fuga = (indice_aviao * 45 + 180) % 360
            diff_angulo = (direcao_fuga - aviao.angulo + 180) % 360 - 180
            aviao.angulo += diff_angulo * 0.3
        else:
            # Persegue com velocidade variável
            aviao.velocidade = aviao.velocidade_max * (0.8 if dist_aviao < ControleAviao.DISTANCIA_IDEAL else 0.6)
            diff_angulo = (indice_aviao * 45)
            if diff_angulo > 180:
                diff_angulo -= 360
            aviao.angulo += diff_angulo * 0.2

    @staticmethod
    def controlar_ia(aviao, sensores_parede, sensores_aviao):
        if not aviao.esta_vivo():
            return
            
        # Avalia a situação atual
        (sensor_parede_proximo, indice_parede_proximo, 
         indice_aviao, dist_aviao, alvo_alinhado, em_perigo) = ControleAviao.avaliar_situacao(sensores_parede, sensores_aviao)
        
        # Comportamento baseado na situação
        if em_perigo:
            ControleAviao.modo_fuga(aviao, sensor_parede_proximo, indice_parede_proximo, indice_aviao)
        elif indice_aviao != -1:
            ControleAviao.modo_combate(aviao, dist_aviao, indice_aviao)
        else:
            # Modo busca
            aviao.velocidade = aviao.velocidade_max * 0.5
            if pygame.time.get_ticks() - aviao.tempo_mudanca_direcao > 2000:
                aviao.angulo += random.choice([-30, 30])
                aviao.tempo_mudanca_direcao = pygame.time.get_ticks()
        
        # Tenta atirar se tiver alvo alinhado e na distância adequada
        if alvo_alinhado and dist_aviao < ControleAviao.DISTANCIA_TIRO:
            aviao.atirar()
        
        # Normaliza o ângulo
        aviao.angulo = aviao.angulo % 360