import random
import numpy as np

class AlgoritmoGenetico:
    def __init__(self):
        self.tamanho_populacao = 6
        self.taxa_mutacao = 0.1
        self.peso_tempo_vida = 0.1    # Reduzido peso do tempo de vida
        self.peso_dano = 20           # Aumentado peso do dano
        self.peso_morte_borda = -200  # Aumentada penalidade por morrer na borda
        self.peso_abates = 100        # Aumentado bônus por abates
        self.peso_sobrevivente = 50   # Reduzido bônus de sobrevivente
        
    def criar_genes_aleatorios(self):
        return {
            'agressividade': random.uniform(0.3, 0.9),  # Aumentado para favorecer combate
            'cautela': random.uniform(0.2, 0.8),        # Reduzido para permitir mais riscos
            'velocidade_base': random.uniform(0.4, 0.8),
            'dist_tiro': random.uniform(0.5, 0.9),      # Aumentado para melhorar precisão
            'dist_fuga': random.uniform(0.2, 0.5)
        }
    
    def mutacao(self, genes):
        genes_mutados = genes.copy()
        for gene in genes_mutados:
            if random.random() < self.taxa_mutacao:
                variacao = random.uniform(-0.1, 0.1)
                genes_mutados[gene] = max(0.1, min(1.0, genes_mutados[gene] + variacao))
        return genes_mutados
    
    def crossover(self, genes1, genes2):
        filho = {}
        for gene in genes1:
            if random.random() < 0.5:
                filho[gene] = genes1[gene]
            else:
                filho[gene] = genes2[gene]
        return filho
    
    def calcular_pontuacao(self, aviao):
        pontuacao = (
            (aviao.tempo_vida * self.peso_tempo_vida) +
            (aviao.dano_causado * self.peso_dano) +
            (aviao.morreu_na_borda * self.peso_morte_borda) +
            (aviao.avioes_abatidos * self.peso_abates) +
            (aviao.bonus_sobrevivente * self.peso_sobrevivente)
        )
        return pontuacao
    
    def selecionar_pais(self, avioes):
        # Ordena aviões usando a nova função de pontuação
        avioes_ordenados = sorted(avioes, key=lambda x: self.calcular_pontuacao(x), reverse=True)
        return avioes_ordenados[:2]