import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scriptsDataset.cleanDataset import clean_dataset

# Prepara o dataset e cria o alvo binario da analise.
df = clean_dataset(pd.read_csv("data/propostas_credito.csv"))

df["mes"] = df["data_entrada"].dt.to_period("M")

# Compara o desempenho de acordo com os meses
monthly = (
    df.groupby("mes").agg(
        propostas=("status_final", "size"),
        contratadas=("status_final", lambda x:(x == "Contratada").sum())
    )
)

monthly["conversao"] = monthly["contratadas"] / monthly["propostas"]

print(monthly)

# Compara o desempenho dos Correspondentes
correspondentes = (
    df[df["canal_origem"] == "correspondente"].groupby("mes").agg(
        propostas=("status_final", "size"),
        contratadas=("status_final", lambda x: (x == "Contratada").sum())
    )
)

correspondentes["conversao"] = correspondentes["contratadas"] / correspondentes["propostas"]

print(correspondentes)

# Compara o desempenho de todos os canais de origem
monthly_channel = (
    df.groupby(["mes", "canal_origem"])
      .agg(
          propostas=("status_final", "size"),
          contratadas=("status_final", lambda x: (x == "Contratada").sum())
      )
)

monthly_channel["conversao"] = (
    monthly_channel["contratadas"] / monthly_channel["propostas"]
)

print(monthly_channel)

# Comparação geral na primeira e segunda metade de 2025
df["periodo"] = np.where(
    df["data_entrada"] < "2025-07-01",
    "2025-H1",
    "2025-H2"
)

comparison = (
    df.groupby("periodo")
      .agg(
          propostas=("status_final", "size"),
          contratadas=("status_final", lambda x: (x == "Contratada").sum())
      )
)

comparison["conversao"] = (
    comparison["contratadas"] / comparison["propostas"]
)

print(comparison)

# Graficos
os.makedirs("graficos", exist_ok=True)

# 1. Número de propostas por mês

propostas = df.groupby("mes").size()

plt.figure(figsize=(10, 5))
plt.plot(
    propostas.index.astype(str),
    propostas.values,
    marker="o"
)
plt.title("Número de propostas por mês")
plt.xlabel("Mês")
plt.ylabel("Propostas")
plt.xticks(rotation=45)
plt.tight_layout()

plt.savefig(
    "graficos/numero_propostas_por_mes.png",
    dpi=300,
    bbox_inches="tight"
)
plt.close()


# 2. Taxa de conversão geral por mês

monthly = (
    df.groupby("mes")
      .agg(
          propostas=("status_final", "size"),
          contratadas=(
              "status_final",
              lambda x: (x == "Contratada").sum()
          )
      )
)

monthly["conversao"] = (
    monthly["contratadas"] / monthly["propostas"] * 100
)

plt.figure(figsize=(10, 5))
plt.plot(
    monthly.index.astype(str),
    monthly["conversao"],
    marker="o"
)
plt.title("Taxa de conversão por mês")
plt.xlabel("Mês")
plt.ylabel("Conversão (%)")
plt.xticks(rotation=45)
plt.tight_layout()

plt.savefig(
    "graficos/taxa_conversao_por_mes.png",
    dpi=300,
    bbox_inches="tight"
)
plt.close()


# 3. Taxa de conversão - Correspondente

correspondentes = (
    df[df["canal_origem"] == "correspondente"]
    .groupby("mes")
    .agg(
        propostas=("status_final", "size"),
        contratadas=(
            "status_final",
            lambda x: (x == "Contratada").sum()
        )
    )
)

correspondentes["conversao"] = (
    correspondentes["contratadas"]
    / correspondentes["propostas"]
    * 100
)

plt.figure(figsize=(10, 5))
plt.plot(
    correspondentes.index.astype(str),
    correspondentes["conversao"],
    marker="o"
)
plt.title("Taxa de conversão - Correspondente")
plt.xlabel("Mês")
plt.ylabel("Conversão (%)")
plt.xticks(rotation=45)
plt.tight_layout()

plt.savefig(
    "graficos/taxa_conversao_correspondente_por_mes.png",
    dpi=300,
    bbox_inches="tight"
)
plt.close()
