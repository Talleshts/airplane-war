import pygame
import math
from config.configuracoes import LARGURA, ALTURA, VERMELHO, VERDE
from entidades.tiro import Tiro
from sistemas.sensores import SistemasSensores

class Aviao:
    def __init__(self, x, y, cor, nome):
        self.x = x
        self.y = y
        self.angulo = 0
        self.velocidade = 0.3
        self.aceleracao = 0.03
        self.velocidade_max = 4
        self.cor = cor
        self.cor_atual = cor
        self.vida = 100
        self.tiros = []
        self.tempo_ultimo_tiro = 0
        self.colidindo = False
        self.tempo_mudanca_direcao = 0
        self.sensores_parede = [0] * 10
        self.sensores_aviao = [0] * 10
        self.pontos_colisao = [None] * 10
        self.alvos_detectados = [None] * 10
        self.nome = nome
        
    def atirar(self):
        tempo_atual = pygame.time.get_ticks()
        if tempo_atual - self.tempo_ultimo_tiro > 500:
            self.tiros.append(Tiro(self.x, self.y, self.angulo, self.cor))
            self.tempo_ultimo_tiro = tempo_atual
            
    def receber_dano(self, dano):
        self.vida -= dano
        if self.vida < 0:
            self.vida = 0
            
    def esta_vivo(self):
        return self.vida > 0
        
    def calcular_distancia_parede(self, angulo):
        dx = math.cos(math.radians(angulo))
        dy = -math.sin(math.radians(angulo))
        
        dist = float('inf')
        if dx > 0:
            dist = min(dist, (LARGURA - self.x) / dx)
        elif dx < 0:
            dist = min(dist, -self.x / dx)
        if dy > 0:
            dist = min(dist, (ALTURA - self.y) / dy)
        elif dy < 0:
            dist = min(dist, -self.y / dy)
            
        return min(1.0, dist / 200)
        
    def calcular_distancia_aviao(self, outro_aviao, angulo):
        if not outro_aviao.esta_vivo():
            return -1
            
        dx = outro_aviao.x - self.x
        dy = outro_aviao.y - self.y
        dist = math.hypot(dx, dy)
        
        angulo_alvo = math.degrees(math.atan2(-dy, dx))
        diff_angulo = abs((angulo - angulo_alvo + 180) % 360 - 180)
        
        if diff_angulo <= 22.5:
            return min(1.0, dist / 200)
        return -1
        
    def mover(self):
        if not self.esta_vivo():
            return
                
        # Atualiza cor quando colidindo
        if self.colidindo:
            self.cor_atual = (0, 0, 0)  # Preto quando colide
            self.receber_dano(0.5)  # Aumentado o dano por colisão
        else:
            self.cor_atual = self.cor
                
        # Aplica movimento com redução quando próximo às bordas
        margem = 50
        fator_reducao = 1.0
        
        if self.x < margem or self.x > LARGURA - margem:
            fator_reducao *= 0.7
        if self.y < margem or self.y > ALTURA - margem:
            fator_reducao *= 0.7
            
        self.x += math.cos(math.radians(self.angulo)) * self.velocidade * fator_reducao
        self.y -= math.sin(math.radians(self.angulo)) * self.velocidade * fator_reducao
            
        # Verifica colisão com bordas e aplica dano
        colidindo_antes = self.colidindo
        self.colidindo = False
        
        if self.x <= 0:
            self.colidindo = True
            self.x = 0
        elif self.x >= LARGURA:
            self.colidindo = True
            self.x = LARGURA
            
        if self.y <= 0:
            self.colidindo = True
            self.y = 0
        elif self.y >= ALTURA:
            self.colidindo = True
            self.y = ALTURA
            
        # Aplica dano extra ao começar a colidir
        if not colidindo_antes and self.colidindo:
            self.receber_dano(5)  # Dano inicial ao colidir
    
    def desenhar(self, tela):
        if not self.esta_vivo():
            return
            
        # Desenha sensores primeiro (para ficarem atrás do avião)
        SistemasSensores.desenhar_sensores(self, tela)
            
        # Desenha tiros
        for tiro in self.tiros:
            tiro.desenhar(tela)
            
        # Desenha avião
        ponta = (
            self.x + math.cos(math.radians(self.angulo)) * 20,
            self.y - math.sin(math.radians(self.angulo)) * 20
        )
        asa_esq = (
            self.x + math.cos(math.radians(self.angulo - 140)) * 20,
            self.y - math.sin(math.radians(self.angulo - 140)) * 20
        )
        asa_dir = (
            self.x + math.cos(math.radians(self.angulo + 140)) * 20,
            self.y - math.sin(math.radians(self.angulo + 140)) * 20
        )
        
        pygame.draw.polygon(tela, self.cor_atual, [ponta, asa_esq, asa_dir])
        
        # Desenha barra de vida
        pygame.draw.rect(tela, VERMELHO, (self.x - 20, self.y - 30, 40, 5))
        pygame.draw.rect(tela, VERDE, (self.x - 20, self.y - 30, 40 * (self.vida/100), 5))
        

        # Desenha nome do avião
        fonte = pygame.font.SysFont("Arial", 12)
        texto = fonte.render(self.nome, True, (0, 0, 0))
        tela.blit(texto, (self.x - 25, self.y - 45))
        
        # Desenha sensores
        #for i in range(8):
         #   angulo_sensor = self.angulo + (i * 45)
          #  comprimento_base = 250  # Comprimento máximo do sensor
           # 
            # Desenha sensores de parede (vermelho)
            #if self.sensores_parede[i] > 0:
            #    comprimento = comprimento_base * self.sensores_parede[i]
                #fim_x = self.x + math.cos(math.radians(angulo_sensor)) * comprimento
                #fim_y = self.y - math.sin(math.radians(angulo_sensor)) * comprimento
                #pygame.draw.line(tela, (255, 0, 0, 128), (self.x, self.y), (fim_x, fim_y), 1)
            
            # Desenha sensores de avião (azul)
            #if self.sensores_aviao[i] > 0:
            #    comprimento = comprimento_base * self.sensores_aviao[i]
                #fim_x = self.x + math.cos(math.radians(angulo_sensor)) * comprimento
                #fim_y = self.y - math.sin(math.radians(angulo_sensor)) * comprimento
                #pygame.draw.line(tela, (0, 0, 255, 128), (self.x, self.y), (fim_x, fim_y), 2)