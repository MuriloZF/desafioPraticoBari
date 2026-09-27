import pandas as pd

df = pd.read_csv("../data/propostas_credito.csv")

print("============= Shape =============")
print(df.shape)
print("============= Types =============")
print(df.dtypes)
print("============= Missing Values =============")
print(f"Absoluto:\n{df.isna().sum()}\nPorcentagem:\n{(df.isna().mean() * 100).round(2)}")
print("============= Unique =============")
print(df.nunique())
print("============= Description =============")
print(df.describe(include="all").T)

categorical = [
    "canal_origem",
    "cidade",
    "uf",
    "tipo_imovel",
    "etapa_max_funil",
    "status_final",
]

print("============= Categorical =============")
for col in categorical:
    print(f"\n============= {col} =============")
    print(df[col].value_counts(dropna=False))


print("============= Análise Status Final =============")
print(f"Taxa de Juros: {pd.crosstab(
    df["status_final"],
    df["taxa_juros_aa"].isna())}")
print(f"Data Assinatura: {pd.crosstab(
      df["status_final"],
      df["data_assinatura_contrato"])}")

print("============= Análise Cidades/UF =============")
print(pd.crosstab(df["cidade"], df["uf"]))

print("============= Análise Funil == 7 =============")
print(df[df["etapa_max_funil"] == 7].T)

print("============= Análise Idade == 14 =============")
print(df[df["idade_cliente"] <= 18].T)

print("============= Análise Valor Imõvel/Valor solicitado =============")
print(df[df["valor_solicitado"] >= df["valor_imovel"]
         .str.replace("R$", "", regex=False)
         .str.strip()
         .astype(float)][[
    "id_proposta",
    "valor_imovel",
    "valor_solicitado",
    "status_final"]])
