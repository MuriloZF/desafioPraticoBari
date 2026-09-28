import pandas as pd
from scriptsDataset.cleanDataset import clean_dataset

df = clean_dataset(pd.read_csv("data/propostas_credito.csv"))

'''
Valores propostos: A taxa_geral foi observada no relacao.py, a recuperacao e o aumento do score que usaremos será 10%
A explicação está em recomendacoes.md, e a linha de raciocíono para chegar nesses valores está documentado em notes.md
'''

TAXA_GERAL = 0.1939
RECUPERACAO_PROPOSTAS = 0.10
AUMENTO_SCORE = 0.10


# Recuperação quantidade de propostas

mensal = (
    df.groupby(df["data_entrada"].dt.to_period("M"))
      .agg(
          propostas=("id_proposta", "size"),
          contratadas=("status_final", lambda x: (x == "Contratada").sum()),
      )
)

mensal["taxa_contratacao"] = mensal["contratadas"] / mensal["propostas"]

propostas_2025 = mensal.loc["2025"]

# Compara o pico de 2025 com a baixa
mes_pico = propostas_2025["propostas"].idxmax()
propostas_pico = propostas_2025.loc[mes_pico, "propostas"]

mes_final = propostas_2025.index[-1]
propostas_final = propostas_2025.iloc[-1]["propostas"]

queda_propostas = propostas_final - propostas_pico
queda_percentual = queda_propostas / propostas_pico

print("\n=== QUEDA NO VOLUME DE PROPOSTAS EM 2025 ===")
print(f"Pico: {mes_pico} - {propostas_pico:.0f} propostas")
print(f"Final: {mes_final} - {propostas_final:.0f} propostas")
print(f"Variação: {queda_propostas:.0f} propostas")
print(f"Variação percentual: {queda_percentual:.2%}")

propostas_recuperadas = abs(queda_propostas) * RECUPERACAO_PROPOSTAS
contratacoes_cenario = propostas_recuperadas * TAXA_GERAL

print("\nCenário de recuperação de 10% da queda:")
print(f"Propostas recuperadas: {propostas_recuperadas:.1f}")
print(f"Contratações adicionais: {contratacoes_cenario:.1f}")

# Foco em clientes com score > 733
grupo_score = df[df["score_credito"] > 733]

propostas_score = len(grupo_score)
contratadas_score = (
    grupo_score["status_final"] == "Contratada"
).sum()

taxa_score = contratadas_score / propostas_score

novas_propostas_score = propostas_score * AUMENTO_SCORE
contratacoes_score = novas_propostas_score * taxa_score

print("\n=== SCORE DE CRÉDITO ===")
print(f"Propostas com score > 733: {propostas_score}")
print(f"Contratadas: {contratadas_score}")
print(f"Taxa de contratação: {taxa_score:.2%}")

print(f"\nCenário de aumento de {AUMENTO_SCORE:.0%}:")
print(f"  Novas propostas: {novas_propostas_score:.1f}")
print(f"  Contratações adicionais estimadas: {contratacoes_score:.1f}")


# Focar em aumentar a taxa de conversão dos correspondentes
correspondentes = df[df["canal_origem"] == "correspondente"]

propostas_correspondentes = len(correspondentes)

contratadas_correspondentes = (
    correspondentes["status_final"] == "Contratada"
).sum()

taxa_correspondentes = (
    contratadas_correspondentes / propostas_correspondentes
)

contratacoes_se_media = propostas_correspondentes * TAXA_GERAL
contratacoes_adicionais = (
    contratacoes_se_media - contratadas_correspondentes
)

print("\n=== CORRESPONDENTES ===")
print(f"Propostas: {propostas_correspondentes}")
print(f"Contratadas: {contratadas_correspondentes}")
print(f"Taxa de contratação: {taxa_correspondentes:.2%}")
print(f"Taxa geral: {TAXA_GERAL:.2%}")
print(f"Diferença: {(taxa_correspondentes - TAXA_GERAL):.2%}")

print("\nCenário caso atingissem a taxa geral:")
print(f"  Contratações esperadas: {contratacoes_se_media:.1f}")
print(f"  Contratações adicionais: {contratacoes_adicionais:.1f}")


# Resumo geral
print("\n=== RESUMO DAS RECOMENDAÇÕES ===")

print(
    f"1. Recuperar volume: "
    f"+{contratacoes_cenario:.1f} contratos "
    f"recuperando 10% da queda."
)

print(
    f"2. Score > 733: "
    f"+{contratacoes_score:.1f} contratos "
    f"com 10% mais propostas nesse grupo."
)

print(
    f"3. Correspondentes: "
    f"+{contratacoes_adicionais:.1f} contratos "
    f"se atingirem a taxa geral."
)
