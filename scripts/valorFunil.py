import os
import pandas as pd
import matplotlib.pyplot as plt
from scriptsDataset.cleanDataset import clean_dataset


df = clean_dataset(pd.read_csv("data/propostas_credito.csv"))

# Ignora todos os empréstimos já concluídos.
perdidas = df[df["etapa_max_funil"] < 6]

# Faz o somatório e a média e monta o ranking (baseado na somatória).
ranking = (
    perdidas
    .groupby("etapa_max_funil")
    .agg(
        propostas=("id_proposta", "count"),
        valor_total=("valor_solicitado", "sum"),
        valor_medio=("valor_solicitado", "mean"),
    )
    .sort_values("valor_total", ascending=False)
)

# Converte o valor total para milhões e limita o número de casas decimais.
ranking["valor_total"] = (ranking["valor_total"] / 1_000_000).round(2)
ranking["valor_medio"] = ranking["valor_medio"].round(2)

print(ranking)

# Gráficos

os.makedirs("graficos", exist_ok=True)


def criar_grafico(coluna, titulo, ylabel, formato_valor, arquivo):
    """Cria um gráfico de barras para uma das categorias do ranking."""
    fig, ax = plt.subplots(figsize=(8, 5))

    valores = ranking[coluna]
    bars = ax.bar(ranking.index.astype(str), valores)

    ax.set_title(titulo)
    ax.set_xlabel("Etapa máxima alcançada")
    ax.set_ylabel(ylabel)

    # Mostra o valor em cima de cada barra.
    for bar, value in zip(bars, valores):
        ax.annotate(
            formato_valor(value),
            xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
            xytext=(0, 3),
            textcoords="offset points",
            ha="center",
            va="bottom",
        )

    fig.tight_layout()
    fig.savefig(arquivo, dpi=300, bbox_inches="tight")
    plt.close(fig)


criar_grafico(
    coluna="valor_total",
    titulo="Valor total solicitado por etapa do funil",
    ylabel="Valor solicitado (R$ milhões)",
    formato_valor=lambda valor: f"R$ {valor:.2f}M",
    arquivo="graficos/valor_solicitado_por_etapa_funil.png",
)

criar_grafico(
    coluna="valor_medio",
    titulo="Valor médio solicitado por etapa do funil",
    ylabel="Valor médio solicitado (R$)",
    formato_valor=lambda valor: f"R$ {valor:,.2f}",
    arquivo="graficos/valor_medio_por_etapa_funil.png",
)
