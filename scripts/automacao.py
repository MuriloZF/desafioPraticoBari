import os
import re
import csv
import html
import logging
import argparse
import tempfile
import pandas as pd
from pathlib import Path
from datetime import date, timedelta
from scriptsDataset.cleanDataset import clean_dataset


ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {
    "id_proposta", "data_entrada", "canal_origem", "valor_imovel",
    "valor_solicitado", "etapa_max_funil", "status_final",
}
OPTIONAL_FOR_CLEANING = {"idade_cliente", "data_assinatura_contrato"}
STATUSES = {
    "Contratada", "Sem retorno", "Desistiu", "Reprovada crédito",
    "Problema garantia", "Documentação pendente",
}
STAGES = {
    1: "Simulação", 2: "Lead", 3: "Análise de crédito",
    4: "Avaliação do imóvel", 5: "Formalização", 6: "Contratação",
}


class InputError(ValueError):
    """A extração não permite gerar métricas confiáveis."""


def configure_logger(log_path: Path) -> logging.Logger:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("automacao_funil")
    logger.setLevel(logging.INFO)
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        handler.close()
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    for handler in (logging.FileHandler(log_path, encoding="utf-8"), logging.StreamHandler()):
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger


def read_input(path: Path, logger: logging.Logger) -> pd.DataFrame:
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as source:
            sample = source.read(8192)
        if not sample.strip():
            raise InputError("Arquivo de entrada vazio.")
        try:
            delimiter = csv.Sniffer().sniff(sample, delimiters=",;").delimiter
        except csv.Error as exc:
            raise InputError("Delimitador não reconhecido; use CSV separado por vírgula ou ponto e vírgula.") from exc
        df = pd.read_csv(path, sep=delimiter, dtype=str, encoding="utf-8-sig", keep_default_na=False)
    except (OSError, UnicodeError, pd.errors.ParserError) as exc:
        raise InputError(f"Não foi possível ler {path}: {exc}") from exc

    df.columns = df.columns.str.strip()
    if df.columns.duplicated().any():
        raise InputError("Cabeçalhos duplicados: " + ", ".join(df.columns[df.columns.duplicated()]))
    missing = REQUIRED - set(df.columns)
    if missing:
        raise InputError("Colunas obrigatórias ausentes: " + ", ".join(sorted(missing)))
    if df.empty:
        raise InputError("O CSV tem cabeçalho, mas não tem propostas.")
    logger.info("Leitura: %d linhas; delimitador %r; %d colunas", len(df), delimiter, len(df.columns))
    for column in sorted(OPTIONAL_FOR_CLEANING - set(df.columns)):
        df[column] = ""
        logger.warning("Coluna opcional %s ausente; preenchida como vazia", column)
    extra = set(df.columns) - REQUIRED - OPTIONAL_FOR_CLEANING
    if extra:
        logger.info("Colunas adicionais preservadas: %s", ", ".join(sorted(extra)))
    return df


def parse_money(value: str) -> float:
    value = str(value).strip().replace("R$", "").strip()
    if re.fullmatch(r"\d+(?:\.\d{1,2})?", value):
        return float(value)
    if re.fullmatch(r"\d{1,3}(?:\.\d{3})+[,]\d{1,2}", value):
        return float(value.replace(".", "").replace(",", "."))
    if re.fullmatch(r"\d+[,]\d{1,2}", value):
        return float(value.replace(",", "."))
    raise ValueError(value)


def parse_dates(values: pd.Series, column: str, allow_blank: bool = False) -> pd.Series:
    values = values.astype(str).str.strip()
    parsed = pd.to_datetime(values, format="%Y-%m-%d", errors="coerce")
    brazilian = pd.to_datetime(values, format="%d/%m/%Y", errors="coerce")
    parsed = parsed.fillna(brazilian)
    bad = parsed.isna() & (values.ne("") if allow_blank else True)
    if bad.any():
        examples = ", ".join(f"linha {i + 2}: {values.iloc[i]!r}" for i in range(len(values)) if bad.iloc[i])
        raise InputError(f"Data inválida em {column}: {examples[:250]}")
    return parsed


def prepare_data(raw: pd.DataFrame, logger: logging.Logger) -> tuple[pd.DataFrame, dict]:
    df = raw.copy()
    for column in REQUIRED:
        if df[column].astype(str).str.strip().eq("").any():
            raise InputError(f"Valores vazios na coluna obrigatória {column}.")
    if df["id_proposta"].duplicated().any():
        raise InputError("id_proposta duplicado; a contagem de propostas ficaria inflada.")

    quality = {}
    for column in ("valor_imovel", "valor_solicitado"):
        try:
            amounts = df[column].map(parse_money)
        except ValueError as exc:
            raise InputError(f"Valor monetário inválido em {column}: {exc}") from exc
        if amounts.le(0).any():
            raise InputError(f"{column} contém valores menores ou iguais a zero.")
        df[column] = amounts.astype(str) if column == "valor_imovel" else amounts

    for column in ("idade_cliente", "etapa_max_funil"):
        values = pd.to_numeric(df[column].replace("", pd.NA), errors="coerce")
        invalid = values.isna() & df[column].astype(str).str.strip().ne("")
        if invalid.any() or (column == "etapa_max_funil" and values.isna().any()):
            raise InputError(f"Formato numérico inválido em {column}.")
        if column == "etapa_max_funil" and (values % 1 != 0).any():
            raise InputError("etapa_max_funil precisa conter números inteiros.")
        df[column] = values

    df["status_final"] = df["status_final"].str.strip()
    unknown = set(df["status_final"]) - STATUSES
    if unknown:
        raise InputError("status_final novo/desconhecido: " + ", ".join(sorted(unknown)))
    stage = df["etapa_max_funil"]
    invalid_stage = ~stage.isin(STAGES) & ~((stage == 7) & df["status_final"].eq("Contratada"))
    if invalid_stage.any():
        raise InputError("etapa_max_funil fora de 1–6 (7 só é aceito para Contratada).")

    entry = parse_dates(df["data_entrada"], "data_entrada")
    signature = parse_dates(df["data_assinatura_contrato"], "data_assinatura_contrato", allow_blank=True)
    quality["datas_formato_br"] = int(df["data_entrada"].str.contains("/", regex=False).sum())
    quality["datas_invertidas"] = int((entry > signature).sum())
    quality["idades_invalidas"] = int(df["idade_cliente"].lt(18).sum())
    quality["etapas_7_corrigidas"] = int(stage.eq(7).sum())
    quality["canais_com_espacos"] = int(df["canal_origem"].ne(df["canal_origem"].str.strip()).sum())
    df["data_entrada"] = entry.dt.strftime("%Y-%m-%d")
    df["data_assinatura_contrato"] = signature.dt.strftime("%Y-%m-%d").fillna("")

    cleaned = clean_dataset(df)
    quality["ltv_acima_60"] = int(cleaned["ltv"].gt(0.60).sum())
    logger.info("Tratamento: %s; nenhuma linha descartada", quality)
    return cleaned, quality


def brl(value: float) -> str:
    return "R$ " + f"{value:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")


def pct(numerator: int, denominator: int) -> str:
    return f"{numerator / denominator:.1%}" if denominator else "—"


def table(headers: list[str], rows: list[list[str]]) -> str:
    heading = "".join(f"<th>{html.escape(value)}</th>" for value in headers)
    body = "".join("<tr>" + "".join(f"<td>{html.escape(str(value))}</td>" for value in row) + "</tr>" for row in rows)
    return f"<table><thead><tr>{heading}</tr></thead><tbody>{body}</tbody></table>"


def build_report(df: pd.DataFrame, quality: dict, input_path: Path, as_of: date) -> tuple[str, date, int]:
    week_start = as_of - timedelta(days=as_of.weekday() + 7)
    week_end = week_start + timedelta(days=6)
    current = df[df["data_entrada"].dt.date.between(week_start, week_end)]
    previous = df[df["data_entrada"].dt.date.between(week_start - timedelta(days=7), week_start - timedelta(days=1))]
    contracts = int(current["status_final"].eq("Contratada").sum())
    previous_contracts = int(previous["status_final"].eq("Contratada").sum())
    requested = float(current["valor_solicitado"].sum())
    lost = current[current["status_final"].ne("Contratada")]
    lost_value = float(lost["valor_solicitado"].sum())
    latest = df["data_entrada"].max().date()

    channel_rows = []
    for channel, group in current.groupby("canal_origem", sort=True):
        count = len(group)
        signed = int(group["status_final"].eq("Contratada").sum())
        channel_rows.append([channel.title(), str(count), str(signed), pct(signed, count)])
    stage_rows = []
    for stage, group in lost.groupby("etapa_max_funil", sort=True):
        stage_rows.append((float(group["valor_solicitado"].sum()), [f"{int(stage)} — {STAGES[int(stage)]}", str(len(group)), brl(float(group["valor_solicitado"].sum()))]))
    stage_rows = [row for _, row in sorted(stage_rows, key=lambda pair: pair[0], reverse=True)]
    notes = []
    if current.empty:
        notes.append("Nenhuma proposta entrou na semana selecionada. Taxas de conversão não são calculadas para base vazia.")
    if latest < week_start:
        notes.append(f"A extração parece desatualizada: a última entrada é de {latest:%d/%m/%Y}.")
    if quality["ltv_acima_60"]:
        notes.append(f"{quality['ltv_acima_60']} propostas da extração completa têm LTV acima de 60%; o relatório não as remove automaticamente.")
    note_html = "".join(f"<li>{html.escape(note)}</li>" for note in notes)
    if not note_html:
        note_html = "<li>Nenhum alerta adicional.</li>"
    quality_rows = [
        ["Linhas lidas / mantidas", f"{len(df)} / {len(df)}"],
        ["Datas de entrada em dd/mm/aaaa", str(quality["datas_formato_br"])],
        ["Datas entrada/assinatura invertidas", str(quality["datas_invertidas"])],
        ["Idades menores que 18 anuladas", str(quality["idades_invalidas"])],
        ["Etapas 7 corrigidas para 6", str(quality["etapas_7_corrigidas"])],
        ["Canais com espaços removidos", str(quality["canais_com_espacos"])],
    ]
    report = f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><title>Funil semanal — {week_start:%d/%m/%Y}</title>
<style>body{{font:16px/1.5 Arial,sans-serif;max-width:1000px;margin:36px auto;padding:0 20px;color:#203047}}h1,h2{{color:#12345a}}.subtitle,.small{{color:#526273}}.cards{{display:flex;flex-wrap:wrap;gap:14px;margin:24px 0}}.card{{background:#edf4fa;border-radius:8px;padding:14px 20px;min-width:170px}}.card strong{{display:block;font-size:1.5em}}table{{border-collapse:collapse;width:100%;margin-bottom:26px}}th,td{{padding:9px 12px;border-bottom:1px solid #d5dfe8;text-align:left}}th{{background:#edf4fa}}.alert{{background:#fff4dc;border-left:4px solid #c47b00;padding:10px 18px}}@media print{{body{{margin:0}}}}</style></head><body>
<h1>Relatório semanal do funil</h1><p class="subtitle">Entradas de {week_start:%d/%m/%Y} a {week_end:%d/%m/%Y} · gerado em {date.today():%d/%m/%Y}</p>
<div class="cards"><div class="card">Propostas<strong>{len(current)}</strong></div><div class="card">Contratadas<strong>{contracts}</strong></div><div class="card">Conversão<strong>{pct(contracts, len(current))}</strong></div><div class="card">Valor solicitado<strong>{brl(requested)}</strong></div><div class="card">Valor não contratado<strong>{brl(lost_value)}</strong></div></div>
<p>Semana anterior: {len(previous)} propostas, {previous_contracts} contratadas, conversão de {pct(previous_contracts, len(previous))}. Comparação por semana de entrada.</p>
<h2>Por canal de origem</h2>{table(['Canal', 'Propostas', 'Contratadas', 'Conversão'], channel_rows or [['Sem dados', '0', '0', '—']])}
<h2>Valor não contratado por etapa máxima</h2>{table(['Etapa', 'Propostas', 'Valor solicitado'], stage_rows or [['Sem dados', '0', brl(0)]])}
<div class="alert"><h2>Observações</h2><ul>{note_html}</ul></div>
<h2>Qualidade da extração</h2>{table(['Verificação', 'Resultado'], quality_rows)}
<p class="small">Fonte: {html.escape(input_path.name)}. Canais foram padronizados em minúsculas. Conversão = propostas com status final “Contratada” / propostas que entraram na semana. O status é o observado na extração atual, não necessariamente o da própria semana. “Valor não contratado” soma o crédito solicitado pelas propostas sem contratação; é potencial, não receita perdida. Etapa máxima 6 sem contratação pode aparecer na tabela. LTV = valor solicitado / valor do imóvel; limite de referência: 60%.</p>
</body></html>"""
    return report, week_start, len(current)


def save_report(output: Path, content: str) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=output.parent, prefix=".funil-", suffix=".tmp", delete=False) as file:
            temporary = Path(file.name)
            file.write(content)
        os.replace(temporary, output)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Gera o relatório da última semana completa (segunda a domingo).")
    parser.add_argument("--input", type=Path, default=ROOT / "data/propostas_credito.csv", help="CSV bruto da extração")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "relatorios", help="Pasta do HTML e do log")
    parser.add_argument("--as-of", type=date.fromisoformat, default=date.today(), metavar="AAAA-MM-DD", help="Data de execução para reproduzir semanas históricas")
    args = parser.parse_args(argv)
    logger = configure_logger(args.output_dir / "automacao.log")
    logger.info("Início: entrada=%s; data de referência=%s", args.input, args.as_of)
    try:
        raw = read_input(args.input, logger)
        cleaned, quality = prepare_data(raw, logger)
        report, week_start, count = build_report(cleaned, quality, args.input, args.as_of)
        output = args.output_dir / f"funil_{week_start:%Y-%m-%d}.html"
        save_report(output, report)
        logger.info("Relatório salvo em %s; %d propostas na semana", output, count)
        if count == 0:
            logger.warning("Semana sem propostas; confira a data de referência e a atualização do CSV")
        return 0
    except (InputError, OSError, ValueError) as exc:
        logger.error("Execução interrompida: %s", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
