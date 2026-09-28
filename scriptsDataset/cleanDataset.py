# Obs: O motivo de cada transformação está explicado melhor no notes.md
import pandas as pd

def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Normaliza canal_origem
    df["canal_origem"] = (
        df["canal_origem"].str.strip().str.lower()    
    )

    # Converte valor_imovel (str -> float)
    df["valor_imovel"] = (
        df["valor_imovel"]
            .str.replace("R$", "", regex=False)
            .str.strip()
            .astype(float)
    )

    # Remove idades inválidas, no caso do dataset a única idade inválida é 14, mas vou generalizar para < 18
    df.loc[df["idade_cliente"] < 18, "idade_cliente"] = pd.NA

    # Havia apenas uma instância em que o etapa_max_funil era maior que 6, como vou substituir direto por um valor especício, irei focar direto na instância em que o valor é 7
    df.loc[df["etapa_max_funil"] == 7, "etapa_max_funil"] = 6

    # Calcula o ltv segundo a fórmula presente no PDF
    df["ltv"] = df["valor_solicitado"] / df["valor_imovel"]

    # Normaliza data_entrada para garantir que todos estejam usando o formato correto (aaaa-mm-dd)
    mask = df["data_entrada"].str.match(r"^\d{2}/\d{2}/\d{4}$")
   
    df.loc[mask, "data_entrada"] = pd.to_datetime(
        df.loc[mask, "data_entrada"],
        format="%d/%m/%Y"
    ).astype("string")

    df["data_entrada"] = pd.to_datetime(df["data_entrada"])
    df["data_assinatura_contrato"] = pd.to_datetime(df["data_assinatura_contrato"])

    mask = df["data_entrada"] > df["data_assinatura_contrato"]

    df.loc[mask, ["data_entrada", "data_assinatura_contrato"]] = (
        df.loc[mask, ["data_assinatura_contrato", "data_entrada"]].to_numpy()
    )
   

    return df
