import pygame
import random
import math

from config.configuracoes import LARGURA, ALTURA

class ControleAviao:
    # Constantes
    DISTANCIA_FUGA = 0.3
    DISTANCIA_MINIMA = 0.4
    DISTANCIA_IDEAL = 0.6
    DISTANCIA_TIRO = 0.8
    DISTANCIA_PAREDE = 0.1

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
    def _ajustar_velocidade(aviao, velocidade_alvo):
        if aviao.velocidade > velocidade_alvo:
            return {'desacelerar': True}
        if aviao.velocidade < velocidade_alvo:
            return {'acelerar': True}
        return {}

    @staticmethod
    def _calcular_direcao(angulo_alvo, angulo_atual):
        diff_angulo = (angulo_alvo - angulo_atual + 180) % 360 - 180
        return {'virar_esquerda': diff_angulo > 0, 'virar_direita': diff_angulo < 0}

    @staticmethod
    def _calcular_direcao_fuga(aviao):
        dx = LARGURA/2 - aviao.x
        dy = ALTURA/2 - aviao.y
        
        if aviao.x < LARGURA * 0.15 or aviao.x > LARGURA * 0.85 or aviao.y < ALTURA * 0.15 or aviao.y > ALTURA * 0.85:
            angulo_base = math.degrees(math.atan2(-dy, dx))
            return angulo_base + (0 if aviao.colidindo else random.uniform(-20, 20))
        return -1

    @staticmethod
    def _processar_modo_fuga(aviao, sensor_parede_proximo, indice_parede_proximo):
        comandos = {}
        
        velocidade_alvo = aviao.velocidade_max * (
            0.8 if aviao.colidindo else
            0.5 + sensor_parede_proximo if sensor_parede_proximo < ControleAviao.DISTANCIA_PAREDE else
            0.4
        )
        comandos.update(ControleAviao._ajustar_velocidade(aviao, velocidade_alvo))

        if sensor_parede_proximo < ControleAviao.DISTANCIA_PAREDE * 1.5:
            direcao = ControleAviao._calcular_direcao_fuga(aviao)
            if direcao == -1:
                direcao = (indice_parede_proximo * 45 + 180 + random.uniform(-20, 20)) % 360
            comandos.update(ControleAviao._calcular_direcao(direcao, aviao.angulo))
            
            if sensor_parede_proximo < ControleAviao.DISTANCIA_PAREDE:
                aviao.receber_dano(0.2)
        
        return comandos

    @staticmethod
    def _processar_ataque(aviao, dist_aviao, alvo_alinhado):
        if not alvo_alinhado or dist_aviao >= aviao.genes['dist_tiro']:
            return {'atirar': False}
            
        chance_tiro = aviao.genes['agressividade']
        if aviao.genes['dist_fuga'] < dist_aviao < aviao.genes['dist_tiro'] * 0.8:
            chance_tiro *= 1.5
            
        return {'atirar': random.random() < chance_tiro}

    @staticmethod
    def _processar_modo_combate(aviao, dist_aviao, indice_aviao, alvo_alinhado):
        comandos = {}
        
        velocidade_alvo = aviao.velocidade_max * (
            0.6 if dist_aviao < aviao.genes['dist_fuga'] else
            0.5 if dist_aviao < aviao.genes['dist_tiro'] * 0.8 else
            0.7
        )
        comandos.update(ControleAviao._ajustar_velocidade(aviao, velocidade_alvo))
        
        if not alvo_alinhado:
            comandos.update(ControleAviao._calcular_direcao(indice_aviao * 45, aviao.angulo))
        
        comandos.update(ControleAviao._processar_ataque(aviao, dist_aviao, alvo_alinhado))
        return comandos

    @staticmethod
    def _processar_modo_busca(aviao):
        comandos = ControleAviao._ajustar_velocidade(aviao, aviao.velocidade_max * 0.6)
        
        tempo_atual = pygame.time.get_ticks()
        if tempo_atual - aviao.tempo_mudanca_direcao > 2000:
            comandos.update({'virar_esquerda': random.random() < 0.5, 'virar_direita': random.random() >= 0.5})
            aviao.tempo_mudanca_direcao = tempo_atual
        
        return comandos

    @staticmethod
    def avaliar_situacao(sensores_parede, sensores_aviao):
        sensor_parede_proximo = min(sensores_parede)
        indice_parede_proximo = sensores_parede.index(sensor_parede_proximo)
        
        indice_aviao = -1
        dist_aviao = float('inf')
        alvo_alinhado = False
        
        for i, valor in enumerate(sensores_aviao):
            if valor > 0 and valor < dist_aviao:
                dist_aviao = valor
                indice_aviao = i
                alvo_alinhado = i in [0, 1, 7]
                
        em_perigo = (sensor_parede_proximo < ControleAviao.DISTANCIA_PAREDE or 
                    (indice_aviao != -1 and dist_aviao < ControleAviao.DISTANCIA_FUGA))
                    
        return sensor_parede_proximo, indice_parede_proximo, indice_aviao, dist_aviao, alvo_alinhado, em_perigo

    @staticmethod
    def controlar_ia(aviao, sensores_parede, sensores_aviao):
        if not aviao.esta_vivo():
            return
            
        situacao = ControleAviao.avaliar_situacao(sensores_parede, sensores_aviao)
        
        comandos = (
            ControleAviao._processar_modo_fuga(aviao, situacao[0], situacao[1]) if situacao[-1] else
            ControleAviao._processar_modo_combate(aviao, situacao[3], situacao[2], situacao[4]) if situacao[2] != -1 else
            ControleAviao._processar_modo_busca(aviao)
        )
        
        if comandos.get('virar_esquerda'): aviao.angulo += 5
        if comandos.get('virar_direita'): aviao.angulo -= 5
        if comandos.get('acelerar'): aviao.velocidade = min(aviao.velocidade + aviao.aceleracao, aviao.velocidade_max)
        if comandos.get('desacelerar'): aviao.velocidade = max(0.3, aviao.velocidade - aviao.aceleracao)
        if comandos.get('atirar'): aviao.atirar()