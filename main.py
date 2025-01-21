import pygame 
import sys
import random
import math
from config.configuracoes import LARGURA, ALTURA, BRANCO, AZUL, VERMELHO, AMARELO, VERDE, VERDE_CLARO, VERMELHO_CLARO, AMARELO_CLARO
from entidades.aviao import Aviao
from sistemas.sensores import SistemasSensores
from sistemas.controles import ControleAviao
from config.genetico import AlgoritmoGenetico

def main():
    pygame.init()
    
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("Guerra de Aviões")
    
    # Variável para controlar modo de jogo
    modo_ia = False  # Começa com jogador
    
    # Criar jogador e inimigos com posições aleatórias
    aviao1 = Aviao(
        random.randint(50, LARGURA-50),  # Posição X aleatória
        random.randint(50, ALTURA-50),   # Posição Y aleatória
        AZUL, 
        "Jogador", 
        None
    )
    
    inimigos = []
    cores = [VERMELHO, AMARELO, VERDE, VERMELHO_CLARO, AMARELO_CLARO, VERDE_CLARO]
    
    for i in range(6):
        inimigos.append(
            Aviao(
                random.randint(50, LARGURA-50),  # Posição X aleatória
                random.randint(50, ALTURA-50),   # Posição Y aleatória
                cores[i],
                f"Inimigo {i+1}",
                None
            )
        )
    
    geracao = 1
    algoritmo_genetico = AlgoritmoGenetico()
    rodando = True
    clock = pygame.time.Clock()
    inimigos_mortos = []  # Lista para guardar inimigos mortos
    
    while rodando:
        
        inimigos = [inimigo for inimigo in inimigos if inimigo.esta_vivo()]

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_TAB:  # Tecla TAB alterna entre modos
                    modo_ia = not modo_ia
                    print(f"Modo {'IA' if modo_ia else 'Jogador'} ativado")
        
        # Controles do jogador (apenas se não estiver em modo IA)
        if not modo_ia:
            teclas = pygame.key.get_pressed()
            ControleAviao.controlar_jogador(aviao1, teclas)
            # Atualiza sensores do jogador
            SistemasSensores.atualizar_sensores(aviao1, inimigos)
        
        # Atualiza sensores e controle dos inimigos
        avioes_ativos = inimigos if modo_ia else inimigos + [aviao1]
        for inimigo in inimigos:
            outros_avioes = [a for a in avioes_ativos if a != inimigo]
            SistemasSensores.atualizar_sensores(inimigo, outros_avioes)
            ControleAviao.controlar_ia(inimigo, inimigo.sensores_parede, inimigo.sensores_aviao)
        
        # Atualização de movimento
        if not modo_ia:
            aviao1.mover()
        for inimigo in inimigos:
            inimigo.mover()
        
        # Atualiza movimento dos tiros
        avioes_com_tiros = [aviao1] + inimigos if not modo_ia else inimigos
        for aviao in avioes_com_tiros:
            aviao.tiros = [tiro for tiro in aviao.tiros if tiro.ativo]
            for tiro in aviao.tiros:
                tiro.mover()
        
        # Verifica colisão de tiros
        todos_avioes = [aviao1] + inimigos if not modo_ia else inimigos
        for atirador in todos_avioes:
            for tiro in atirador.tiros:
                for alvo in todos_avioes:
                    if alvo != atirador and tiro.ativo and alvo.esta_vivo():
                        if math.hypot(tiro.x - alvo.x, tiro.y - alvo.y) < 20:
                            alvo.receber_dano(10)
                            tiro.ativo = False
                            if atirador != aviao1:  # Se foi um inimigo que acertou
                                atirador.dano_causado += 10
                                if not alvo.esta_vivo():
                                    atirador.avioes_abatidos += 1
                            break
        
        # Limpa a tela
        tela.fill(BRANCO)
        
        # Desenha todos os aviões e seus tiros
        avioes_para_desenhar = [aviao1] + inimigos if not modo_ia else inimigos
        for aviao in avioes_para_desenhar:
            if aviao.esta_vivo():
                aviao.desenhar(tela)
                for tiro in aviao.tiros:
                    if tiro.ativo:
                        tiro.desenhar(tela)
        
        # Desenha informações da geração
        fonte = pygame.font.SysFont("Arial", 20)
        texto_geracao = fonte.render(f"Geração: {geracao}", True, (0, 0, 0))
        texto_modo = fonte.render(f"Modo: {'IA' if modo_ia else 'Jogador'}", True, (0, 0, 0))
        texto_avioes_vivos = fonte.render(f"Aviões Vivos: {len(inimigos)}", True, (0, 0, 0))
        tela.blit(texto_geracao, (10, 10))
        tela.blit(texto_modo, (10, 35))
        tela.blit(texto_avioes_vivos, (10, 60))
        
        pygame.display.flip()
        clock.tick(60)
        
        # Atualiza pontuação dos inimigos vivos
        for inimigo in inimigos:
            inimigo.atualizar_pontuacao()
        
        # Se todos os inimigos morreram ou sobrou apenas um, finaliza a geração
        if len(inimigos) <= 1:
            print(f"Geração {geracao} finalizada")
            
            # Se sobrou um vivo, adiciona ele à lista de mortos
            if len(inimigos) == 1:
                ultimo_sobrevivente = inimigos[0]
                ultimo_sobrevivente.bonus_sobrevivente = 1
                inimigos_mortos.append(ultimo_sobrevivente)
                inimigos.clear()
            
            # Mostra estatísticas da geração
            for inimigo in inimigos_mortos:
                print(f"{inimigo.nome}: Pontuação={inimigo.pontuacao}, "
                    f"Dano={inimigo.dano_causado}, "
                    f"Tempo={inimigo.tempo_vida}, "
                    f"Abates={inimigo.avioes_abatidos}, "
                    f"Sobrevivente={'Sim' if inimigo.bonus_sobrevivente else 'Não'},"
                    f"Bonus={inimigo.bonus_sobrevivente}")
            
            # Cria nova geração
            novos_inimigos = []
            cores = [VERMELHO, AMARELO, VERDE, VERMELHO_CLARO, AMARELO_CLARO, VERDE_CLARO]
            
            if len(inimigos_mortos) >= 2:
                # Seleciona os melhores antes de criar nova geração
                melhores = algoritmo_genetico.selecionar_pais(inimigos_mortos)
                
                for i in range(6):
                    if i < 2:  # Mantém os dois melhores
                        genes = melhores[i].genes
                    else:  # Cria novos por crossover e mutação
                        genes = algoritmo_genetico.crossover(melhores[0].genes, melhores[1].genes)
                        genes = algoritmo_genetico.mutacao(genes)
                    
                    novo_inimigo = Aviao(
                        random.randint(50, LARGURA-50),
                        random.randint(50, ALTURA-50),
                        cores[i],
                        f"Inimigo {i+1}",
                        genes
                    )
                    novos_inimigos.append(novo_inimigo)
            else:
                # Se não tiver sobreviventes suficientes, cria nova geração com genes aleatórios
                for i in range(6):
                    novo_inimigo = Aviao(
                        random.randint(50, LARGURA-50),
                        random.randint(50, ALTURA-50),
                        cores[i],
                        f"Inimigo {i+1}",
                        None  # Genes serão criados aleatoriamente no construtor
                    )
                    novos_inimigos.append(novo_inimigo)
            
            inimigos = novos_inimigos
            geracao += 1
            inimigos_mortos = []  # Limpa lista de mortos
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()