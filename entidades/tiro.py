import pygame
import math
from config.configuracoes import LARGURA, ALTURA

class Tiro:
    def __init__(self, x, y, angulo, cor):
        self.x = x
        self.y = y
        self.angulo = angulo
        self.velocidade = 10
        self.cor = cor
        self.ativo = True
        
    def mover(self):
        self.x += math.cos(math.radians(self.angulo)) * self.velocidade
        self.y -= math.sin(math.radians(self.angulo)) * self.velocidade
        
        if self.x < 0 or self.x > LARGURA or self.y < 0 or self.y > ALTURA:
            self.ativo = False
            
    def desenhar(self, tela):
        if self.ativo:
            pygame.draw.circle(tela, self.cor, (int(self.x), int(self.y)), 3)
            #Fazer um contorno do tiro com a cor escura
            pygame.draw.circle(tela, (0, 0, 0), (int(self.x), int(self.y)), 3, 1)
