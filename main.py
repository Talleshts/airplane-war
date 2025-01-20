import pygame 
import sys
import math
from config.configuracoes import LARGURA, ALTURA, BRANCO, AZUL, VERMELHO, AMARELO, VERDE, VERDE_CLARO, VERMELHO_CLARO, AMARELO_CLARO
from entidades.aviao import Aviao
from sistemas.sensores import SistemasSensores
from sistemas.controles import ControleAviao

def main():
    pygame.init()
    
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("Guerra de Aviões")
    
    # Criar jogador e inimigos
    aviao1 = Aviao(100, 300, AZUL, "Jogador")
    inimigos = [
        Aviao(700, 300, VERMELHO, "Inimigo 1"),
        Aviao(600, 100, AMARELO, "Inimigo 2"),
        Aviao(100, 500, VERDE, "Inimigo 3"),        
        Aviao(740, 200, VERMELHO_CLARO, "Inimigo 4"),
        Aviao(200, 80, AMARELO_CLARO, "Inimigo 5"),
        Aviao(500, 500, VERDE_CLARO, "Inimigo 6")
    ]
    
    rodando = True
    clock = pygame.time.Clock()
    
    while rodando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
                
        # Controles do jogador
        teclas = pygame.key.get_pressed()
        ControleAviao.controlar_jogador(aviao1, teclas)
        
        # Atualiza sensores do jogador
        SistemasSensores.atualizar_sensores(aviao1, inimigos)
            
        # Atualiza sensores e controle dos inimigos
        for inimigo in inimigos:
            outros_avioes = [a for a in inimigos + [aviao1] if a != inimigo]
            SistemasSensores.atualizar_sensores(inimigo, outros_avioes)
            ControleAviao.controlar_ia(inimigo, inimigo.sensores_parede, inimigo.sensores_aviao)
        
        # Atualização de movimento
        aviao1.mover()
        for inimigo in inimigos:
            inimigo.mover()
            
        # Atualiza movimento dos tiros
        for aviao in [aviao1] + inimigos:
            # Remove tiros inativos
            aviao.tiros = [tiro for tiro in aviao.tiros if tiro.ativo]
            # Move tiros ativos
            for tiro in aviao.tiros:
                tiro.mover()
        
        todos_avioes = [aviao1] + inimigos
        
        # Verifica colisão de tiros entre todos os aviões
        for atirador in todos_avioes:
            for tiro in atirador.tiros:
                for alvo in todos_avioes:
                    if alvo != atirador and tiro.ativo and alvo.esta_vivo():
                        if math.hypot(tiro.x - alvo.x, tiro.y - alvo.y) < 20:
                            alvo.receber_dano(10)
                            tiro.ativo = False
                            break
        
        # Remover inimigos mortos
        inimigos = [inimigo for inimigo in inimigos if inimigo.esta_vivo()]
        
        # Verifica se o jogador foi atingido
        if aviao1.vida <= 0:
            rodando = False
            #mostrar tela de game over
            fonte = pygame.font.SysFont("Arial", 24)
            texto = fonte.render("Game Over", True, (0, 0, 0))
            tela.blit(texto, (LARGURA // 2 - 50, ALTURA // 2 - 12))
            pygame.display.flip()
            pygame.time.wait(3000)

        # Desenho
        tela.fill(BRANCO)
        aviao1.desenhar(tela)
        for inimigo in inimigos:
            inimigo.desenhar(tela)
            
        pygame.display.flip()
        clock.tick(60)
    


    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()