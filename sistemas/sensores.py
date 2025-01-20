import math
import pygame
from config.configuracoes import LARGURA, ALTURA, VERMELHO, AZUL, AMARELO, VERDE

class SistemasSensores:
    @staticmethod
    def calcular_distancia_parede(x, y, angulo):
        # Converte ângulo para radianos e calcula direção
        dx = math.cos(math.radians(angulo))
        dy = -math.sin(math.radians(angulo))
        
        # Calcula distância para cada parede
        dist_direita = (LARGURA - x) / dx if dx > 0 else float('inf')
        dist_esquerda = -x / dx if dx < 0 else float('inf')
        dist_inferior = (ALTURA - y) / dy if dy > 0 else float('inf')
        dist_superior = -y / dy if dy < 0 else float('inf')
        
        # Encontra a menor distância válida
        dist = min(
            d for d in [dist_direita, dist_esquerda, dist_inferior, dist_superior]
            if d >= 0
        )
        
        # Normaliza a distância (250 pixels é o alcance máximo)
        return min(1.0, dist / 250)
    
    @staticmethod
    def calcular_distancia_aviao(x, y, angulo, avioes_proximos):
        if not isinstance(avioes_proximos, list):
            avioes_proximos = [avioes_proximos]
            
        menor_dist = -1
        alvo_mais_proximo = None
        
        for outro_aviao in avioes_proximos:
            if not outro_aviao.esta_vivo():
                continue
                
            dx = outro_aviao.x - x
            dy = outro_aviao.y - y
            dist = math.hypot(dx, dy)
            
            angulo_alvo = math.degrees(math.atan2(-dy, dx))
            diff_angulo = abs((angulo - angulo_alvo + 180) % 360 - 180)
            
            if diff_angulo <= 22.5:  # Cone de visão de 45 graus
                dist_normalizada = min(1.0, dist / 250)
                if menor_dist == -1 or dist_normalizada < menor_dist:
                    menor_dist = dist_normalizada
                    alvo_mais_proximo = outro_aviao
                    
        return menor_dist, alvo_mais_proximo
    
    #Sensores mais antigos (fixos)
    # def desenhar_sensores(self, tela):
    #     if not self.esta_vivo():
    #         return
            
    #     comprimento_base = 250  # Comprimento máximo do sensor
        
    #     # Desenha os 11 sensores
    #     for i in range(11):
    #         angulo_sensor = self.angulo + (i * 45)
            
    #         # Desenha sensores de parede (vermelho)
    #         if self.sensores_parede[i] > 0:
    #             comprimento = comprimento_base * (1 - self.sensores_parede[i])
    #             fim_x = self.x + math.cos(math.radians(angulo_sensor)) * comprimento
    #             fim_y = self.y - math.sin(math.radians(angulo_sensor)) * comprimento
                
    #             cor = VERMELHO
    #             if self.sensores_parede[i] < 0.3:  # Muito próximo
    #                 cor = (255, 0, 0)  # Vermelho mais intenso
    #             elif self.sensores_parede[i] < 0.7:
    #                 cor = (255, 165, 0)  # Laranja
                

    #             pygame.draw.line(tela, cor, (self.x, self.y), (fim_x, fim_y), 2)
    #             pygame.draw.circle(tela, cor, (int(fim_x), int(fim_y)), 4)
            
    #         # Desenha sensores de avião (azul)
    #         if self.sensores_aviao[i] > 0:
    #            comprimento = comprimento_base * (1 - self.sensores_aviao[i])
    #            fim_x = self.x + math.cos(math.radians(angulo_sensor)) * comprimento
    #            fim_y = self.y - math.sin(math.radians(angulo_sensor)) * comprimento
                
    #            cor = AZUL
    #            if i in [0, 1, 7]:  # Sensores frontais
    #             cor = VERDE if self.sensores_aviao[i] > 0.3 else AMARELO
                   
    #             pygame.draw.line(tela, cor, (self.x, self.y), (fim_x, fim_y), 2)
    #             pygame.draw.circle(tela, cor, (int(fim_x), int(fim_y)), 4)

    #Sensores mais dinamicos
    def desenhar_sensores(self, tela):
        if not self.esta_vivo():
            return
            
        comprimento_base = 250
        
        # Desenha os 10 sensores (36 graus entre cada)
        for i in range(10):
            angulo_sensor = self.angulo + (i * 36)  # 360/10 = 36 graus
            
            # Desenha sensores de parede
            if self.sensores_parede[i] > 0:
                comprimento = comprimento_base * (1 - self.sensores_parede[i])
                fim_x = self.x + math.cos(math.radians(angulo_sensor)) * comprimento
                fim_y = self.y - math.sin(math.radians(angulo_sensor)) * comprimento
                
                # Cor dinâmica baseada na distância
                intensidade = int(255 * (1 - self.sensores_parede[i]))
                cor = (intensidade, 0, 0, max(50, intensidade))  # Vermelho com alpha
                
                pygame.draw.line(tela, cor, (self.x, self.y), (fim_x, fim_y), 2)
                if self.pontos_colisao[i]:
                    pygame.draw.circle(tela, cor, (int(fim_x), int(fim_y)), 4)
            
            # Desenha sensores de avião
            if self.sensores_aviao[i] > 0:
                comprimento = comprimento_base * (1 - self.sensores_aviao[i])
                fim_x = self.x + math.cos(math.radians(angulo_sensor)) * comprimento
                fim_y = self.y - math.sin(math.radians(angulo_sensor)) * comprimento
                
                # Cor dinâmica baseada na distância e posição
                if i in [0, 1, 9]:  # Sensores frontais (ajustado para 10 sensores)
                    intensidade = int(255 * (1 - self.sensores_aviao[i]))
                    cor = (0, intensidade, 0, max(50, intensidade))  # Verde com alpha
                else:
                    cor = (0, 0, 255, 128)  # Azul com alpha
                
                pygame.draw.line(tela, cor, (self.x, self.y), (fim_x, fim_y), 2)
                if self.alvos_detectados[i]:
                    pygame.draw.circle(tela, cor, (int(fim_x), int(fim_y)), 4)

    @staticmethod
    def atualizar_sensores(aviao, avioes_proximos):
        sensores_parede = []
        sensores_aviao = []
        pontos_colisao = []
        alvos_detectados = []
        
        for i in range(10):  # 10 sensores distribuídos em 360 graus
            angulo_sensor = aviao.angulo + (i * 36)  # 360/10 = 36 graus
            dist_parede = SistemasSensores.calcular_distancia_parede(aviao.x, aviao.y, angulo_sensor)
            dist_aviao, alvo = SistemasSensores.calcular_distancia_aviao(aviao.x, aviao.y, angulo_sensor, avioes_proximos)
            
            sensores_parede.append(dist_parede)
            pontos_colisao.append(None)  # Simplificado para não usar pontos de colisão
            sensores_aviao.append(dist_aviao)
            alvos_detectados.append(alvo)
            
        # Atualiza os atributos do avião
        aviao.sensores_parede = sensores_parede
        aviao.pontos_colisao = pontos_colisao
        aviao.sensores_aviao = sensores_aviao
        aviao.alvos_detectados = alvos_detectados
        
        return sensores_parede, sensores_aviao