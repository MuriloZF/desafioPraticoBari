import pandas as pd
from sklearn.preprocessing import OrdinalEncoder
from scriptsDataset.cleanDataset import clean_dataset
from sklearn.feature_selection import mutual_info_classif


# Prepara o dataset e cria o alvo binario da analise.
df = clean_dataset(pd.read_csv("data/propostas_credito.csv"))
df["contratada"] = df["status_final"].eq("Contratada")

# Somente caracteristicas conhecidas na entrada da proposta.
categorical_columns = [
    "canal_origem",
    "cidade",
    "uf",
    "tipo_imovel",
    "flag_cliente_recorrente",
    "prazo_meses",
]

numeric_columns = [
    "score_credito",
    "ltv",
    "valor_imovel",
    "valor_solicitado",
    "renda_mensal_declarada",
    "idade_cliente",
]

features = categorical_columns + numeric_columns
X = df[features].copy()
y = df["contratada"]

# Para Mutual Information, os codigos apenas representam categorias.
encoder = OrdinalEncoder()
X[categorical_columns] = encoder.fit_transform(X[categorical_columns])

# A idade invalida virou nula durante a limpeza. Aqui ela e retirada apenas
# do calculo de Mutual Information.
X_mi = X.dropna()
y_mi = y.loc[X_mi.index]

categorical_mask = X_mi.columns.isin(categorical_columns)
mi = mutual_info_classif(
    X_mi,
    y_mi,
    discrete_features=categorical_mask,
    random_state=42,
)

mi_scores = (
    pd.DataFrame({
        "caracteristica": X_mi.columns,
        "mutual_information": mi,
    })
    .sort_values("mutual_information", ascending=False)
    .reset_index(drop=True)
)

print(f"Taxa geral de contratacao: {df['contratada'].mean():.2%}")
print("\nRanking de associacao (Mutual Information):")
print(mi_scores.to_string(index=False))


def resumo_taxa(grupo):
    """Resume quantidade e taxa de contratacao de cada grupo."""
    resumo = (
        df.groupby(grupo, observed=True)["contratada"]
        .agg(propostas="size", contratadas="sum", taxa_contratacao="mean")
    )
    resumo["taxa_contratacao_%"] = resumo["taxa_contratacao"] * 100
    resumo["diferenca_da_media_pp"] = (
        resumo["taxa_contratacao"] - df["contratada"].mean()
    ) * 100

    return resumo.drop(columns="taxa_contratacao").round(2)


# Estas tabelas mostram a direcao da associacao, algo que a MI nao mostra.
for column in categorical_columns:
    print(f"\nTaxa de contratacao por {column}:")
    print(
        resumo_taxa(column)
        .sort_values("taxa_contratacao_%", ascending=False)
        .to_string()
    )

# Para variaveis numericas, divide as propostas em cinco grupos de mesmo tamanho.
for column in numeric_columns:
    faixas = pd.qcut(df[column], q=5, duplicates="drop")
    print(f"\nTaxa de contratacao por faixa de {column}:")
    print(resumo_taxa(faixas).to_string())
