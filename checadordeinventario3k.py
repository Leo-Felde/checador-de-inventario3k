#!/usr/bin/env python3
"""
  Feito com muito ódio por DrLegato com notepad++ porque o TI (Arcontes do Demiurgo) não me deixa usar o VStudio sem ter que passar por 15 anos de burocracia
  
  
 eu fiz essa merda inteira em uma hora e meia com auxílio de 2 latas de redbull e 1 camel amarelo
 não houve qualquer tipo de teste depois de feito
 ele funcionou pra mim, pode ser que ele reverta a entropia local de onde você rodar
 
 
 eu não garanto nada, honestamente.
 
 vvvvvvvvvvvvvvvvvvvvvvvvv


checadordeinventario3k.py

O que essa porra faz?

Escaneia arquivo procurando:
- linhas duplicadas (string exata duas vezes)
- IDs disformes (baseado em regras que tu definir)
- quase-duplicados (mesmos digitos apos normalização)

Essa merda suporta:
- .txt / .csv / .tsv / plain text no geral
- .docx (via python-docx)
- o resto tá na mão de Deus, Odin, Rah, Sophia, Shiva, que seja.

Como usar essa caralha:
  python checadordeinventario3k.py path/to/file.docx
  python checadordeinventario3k.py path/to/file.txt --expected-length 9
  python checadordeinventario3k.py path/to/file.txt --csv-out report_prefix

Dependencia pra .docx:
  pip install python-docx
  
  
  
  'ain mas seu codigo ta muito sujo'
  ta funcionando entao nao mexe
  'ain mas pra que usar python? usa [insira linguagem aqui]'
  parceiro, eu sou um bibliotecário que tem dois certificados de programação, um é com python e o outro é ruby. se tu quer tanto mudar a linguagem usada, fique à vontade.
  forte abraço, tomara que nada exploda
  
  boa noite, boa sorte,
  
  DrLegato
"""

from __future__ import annotations

import argparse
import csv
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable, List, Tuple

# ---------- os helpers ----------

print ("checadordeinventario3000 \n\n feito por DrLegato \n\n")

def ler_linhas_txt(path: Path) -> List[str]:
    # manter as linhas originais, limpar whitespace e newline
    text = path.read_text(encoding="utf-8", errors="replace")
    return [line.rstrip("\n\r") for line in text.splitlinhas()]

def ler_linhas_docx(path: Path) -> List[str]:
    try:
        from docx import Document
    except ImportError as e:
        raise SystemExit(
            "Baixa a dependencia pra .docx parceiro. pip install python-docx"
        ) from e

    doc = Document(str(path))
    linhas: List[str] = []
    for p in doc.paragraphs:
        # preservar conteudo mas cortar espaçamento de doc
        s = p.text.strip()
        if s:
            linhas.append(s)
    return linhas

def ler_linhas(path: Path) -> List[str]:
    suffix = path.suffix.lower()
    if suffix == ".docx":
        return ler_linhas_docx(path)
    else:
        return ler_linhas_txt(path)

# ---------- regras de ID ----------

def normalize_digits(s: str) -> str:
    """Rerém só os dígitos. Útil pra detectar quase-duplicados."""
    return re.sub(r"\D+", "", s)

def is_all_digits(s: str) -> bool:
    return bool(re.fullmatch(r"\d+", s))

def achar_candidatos_tokens(line: str) -> List[str]:
    """
    Transforma a linha num token pra procurar pedaços de ID
    Se seu arquivo tem um ID por linha, tá ótimo
    SE tiver mais de um token por linha, ajuda
    de resto, reza, amigão
    """
    # Divide o whitespace e separadores comuns, mas mantém tokens esquisitos intactos
    return [t for t in re.split(r"[\s,;|]+", line.strip()) if t]

def classificar_token(token: str, expected_len: int) -> Tuple[bool, str]:
    """
    Return (is_valid, motivo).
    Rules (ajustáveis):
    - deve ser exatamente do tamanho de expected_len
    - sem letras
    - sem fragmentos de encoding %
    - sem espaços 
    """
    if not token:
        return False, "token vazio"

    if "%" in token:
        return False, "contém '%' (possível URL-encoding como %3)"

    if re.search(r"[A-Za-z]", token):
        return False, "contém letras"

    if not is_all_digits(token):
        return False, "contains caracteres não-dígito"

    if len(token) != expected_len:
        return False, f"len errado (tenho {len(token)}, esperava {expected_len})"

    # opcional: proibir todos os IDs não-zero
    if set(token) == {"0"}:
        return False, "tudo zero"

    return True, "ok, tudo tranquilo"

# ---------- Reportando ----------

def report_duplicados_exatos(linhas: List[str]) -> List[Tuple[str, int]]:
    counts = Counter(linhas)
    duplis = [(line, c) for line, c in counts.items() if c > 1 and line.strip() != ""]
    # sort por count descendente e depois value
    duplis.sort(key=lambda x: (-x[1], x[0]))
    return duplis

def scan_tokens(
    linhas: List[str],
    expected_len: int,
) -> Tuple[
    List[Tuple[int, str, str, str]],  # (line_no, raw_line, token, razão) malformado
    Counter,                           # contagens de tokens validos
    defaultdict,                       # digits_normalizados -> lista de (line_no, token)
]:
    malformado: List[Tuple[int, str, str, str]] = []
    valido_counts: Counter = Counter()
    near: defaultdict = defaultdict(list)

    for idx, raw in enumerate(linhas, start=1):
        if not raw.strip():
            continue
#se essa porra nao funcionar eu irei enfiar 5 metros de arame farmado na minha uretra
        for tok in achar_candidatos_tokens(raw):
            ok, reason = classificar_token(tok.strip(), expected_len)
            if ok:
                valido_counts[tok] += 1
                near[normalize_digits(tok)].append((idx, tok))
            else:
                # se voce quiser só classificar tokens "ID Looking", gate aqui
                #por hora, reporta qualquer coisa não vazia que não é um ID válido
                malformado.append((idx, raw, tok, reason))

    return malformado, valido_counts, near

def print_sumario(
    exato_duplis: List[Tuple[str, int]],
    malformado: List[Tuple[int, str, str, str]],
    valido_counts: Counter,
    near: defaultdict,
):
    # linhas exatamente duplicadas
    print("\n=== Exatas LINHAS duplicadas (mesma linha inteira) ===")
    if not exato_duplis:
        print("Nenhuma. nice.")
    else:
        for line, c in exato_duplis[:50]:
            print(f"[x{c}] {line}")
        if len(exato_duplis) > 50:
            print(f"... plus {len(exato_duplis) - 50} more")

    # IDs Duplicados (tokens validos repetidos)
    dupli_valid = [(tok, c) for tok, c in valido_counts.items() if c > 1]
    dupli_valid.sort(key=lambda x: (-x[1], x[0]))
    print("\n=== Duplicate VALID IDs (same token repeated) ===")
    if not dupli_valid:
        print("None.")
    else:
        for tok, c in dup_valid[:50]:
            print(f"[x{c}] {tok}")
        if len(dupli_valid) > 50:
            print(f"... plus {len(dup_valid) - 50} more")

    # malformado
    print("\n=== malformado tokens (first 50) ===")
    if not malformado:
        print("None.")
    else:
        for (line_no, raw_line, tok, reason) in malformado[:50]:
            print(f"Line {line_no}: token={tok!r} -> {reason} | line={raw_line!r}")
        if len(malformado) > 50:
            print(f"... plus {len(malformado) - 50} more")

    # quase-duplicados: mesmos digitos depois de tirar nao digitos, mas alguns tokens diferentes
    print("\n=== grupos quase duplicados (mesmos digitos depois da normalização) ===")
    groups = []
    for norm, occurrences in near.items():
        unique_tokens = sorted(set(t for _, t in occurrences))
        if len(unique_tokens) > 1:
            groups.append((norm, unique_tokens, occurrences))
    groups.sort(key=lambda x: (-len(x[2]), x[0]))

    if not groups:
        print("Nenhum. nice")
    else:
        for norm, unique_tokens, occ in groups[:30]:
            print(f"Digits: {norm}")
            print(f"  Variants: {unique_tokens}")
            print(f"  Occurrences: {len(occ)} (showing up to 10): {occ[:10]}")
        if len(groups) > 30:
            print(f"... plus {len(groups) - 30} more groups")

def escrever_csv_reports(prefix: str,
                      exato_duplis: List[Tuple[str, int]],
                      malformado: List[Tuple[int, str, str, str]],
                      valido_counts: Counter):
    # duplicates of whole linhas
    with open(f"{prefix}_linhas_duplicadas.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["line", "count"])
        for line, c in exato_duplis:
            w.writerow([line, c])

    # malformado tokens
    with open(f"{prefix}_malformado.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["line_no", "raw_line", "token", "reason"])
        for row in malformado:
            w.writerow(row)

    # valid duplicates
    dup_valid = [(tok, c) for tok, c in valido_counts.items() if c > 1]
    dup_valid.sort(key=lambda x: (-x[1], x[0]))
    with open(f"{prefix}_duplicados_valid_ids.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "count"])
        for tok, c in dup_valid:
            w.writerow([tok, c])

# ---------- Principal ----------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path", help="path do arquivo (.txt/.csv/.docx suportado)")
    ap.add_argument("--comprimento_esperado", type=int, default=9,
                    help="Comprimento do ID esperado (digitos). Default: 9")
    ap.add_argument("--csv-out", default=None,
                    help="Se setado, escreve um relatório CSV usando esse prefixo")
    args = ap.parse_args()

    path = Path(args.path)
    if not path.exists():
        raise SystemExit(f"404 diretório não encontrado em: {path}")

    linhas = ler_linhas(path)

    exato_duplis = report_duplicados_exatos(linhas)
    malformado, valido_counts, near = scan_tokens(linhas, expected_len=args.comprimento_esperado)

    print(f"Scanned: {path}")
    print(f"total de linhas não vazias: {sum(1 for l in linhas if l.strip())}")
    print(f"Total de tokens detectados: {sum(len(achar_candidatos_tokens(l)) for l in linhas if l.strip())}")
    print(f"IDs válidos encontrados: {sum(valido_counts.values())} (unique: {len(valido_counts)})")
    print(f"tokens malformados encontrados: {len(malformado)}")

    print_sumario(exato_duplis, malformado, valido_counts, near)

    if args.csv_out:
        write_csv_reports(args.csv_out, exato_duplis, malformado, valido_counts)
        print(f"\nEscreveu relatórios CSV com prefix: {args.csv_out}_*.csv")

if __name__ == "__main__":
    main()
