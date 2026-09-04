"""
gerar_app.py  —  Atualiza a lista de cidades do app "Nossos Passeios".

A IDEIA
-------
Você continua editando as cidades no lugar que já conhece (Excel, CSV ou um
backup .json exportado pelo próprio app). Roda este script e ele gera de novo
o HTML bonito, pronto pra abrir no celular, com a lista atualizada.

Ele NÃO mexe no visual — só troca os dados. Pra mudar cores/textos, edite o
próprio arquivo .html (é um arquivo só).

COMO USAR (no terminal, na mesma pasta dos arquivos)
----------------------------------------------------
    python gerar_app.py
        Lê 'viagens_atualizado.xlsx' e atualiza 'index.html'.

    python gerar_app.py minha_lista.csv
        Lê de um CSV.

    python gerar_app.py backup.json app_novo.html
        Lê de um backup do app e grava num HTML novo (sem sobrescrever o atual).

ROTA / ORIGEM DO GOOGLE MAPS
----------------------------
    Por padrão, o botão "Ver rota" sai de ONDE VOCÊS ESTIVEREM (usa o GPS do
    celular). O script reforça isso toda vez que regenera. Se um dia quiser
    fixar a saída num lugar, é só passar --origem:

    python gerar_app.py --origem "Franco da Rocha, SP"
        Faz a rota sair sempre de Franco da Rocha.

COLUNAS ACEITAS NA PLANILHA (maiúsculas/minúsculas tanto faz)
-------------------------------------------------------------
    CIDADE     (ou 'cidade')                 -> nome da cidade          [obrigatório]
    KM         (ou 'km')                      -> distância em km          [obrigatório]
    VISITAMOS  (ou 'visitado' / 'visitada')   -> S/N, Sim/Não, 1/0, True  [opcional]

REQUISITOS
----------
    pip install pandas openpyxl
"""

import json
import re
import argparse
from pathlib import Path


# ---------- leitura dos dados ----------

def _achar_coluna(colunas, *nomes):
    """Acha o nome real da coluna ignorando maiúsculas/espaços."""
    mapa = {str(c).lower().strip(): c for c in colunas}
    for n in nomes:
        if n in mapa:
            return mapa[n]
    return None


def _para_bool(valor):
    """Converte S/Sim/1/True/x -> True; o resto -> False."""
    return str(valor).strip().lower() in (
        "s", "sim", "true", "1", "x", "verdadeiro", "y", "yes"
    )


def _limpar_km(valor):
    """Aceita '52,3' (vírgula) ou '52.3' (ponto)."""
    return round(float(str(valor).replace(",", ".").strip()), 1)


def ler_dados(caminho):
    """Lê .xlsx, .csv ou .json e devolve uma lista de dicts padronizada."""
    caminho = Path(caminho)
    if not caminho.exists():
        raise FileNotFoundError(f"Não encontrei o arquivo: {caminho}")

    ext = caminho.suffix.lower()

    if ext == ".json":
        dados = json.loads(caminho.read_text(encoding="utf-8"))
        lista = [{
            "cidade": str(d.get("cidade", d.get("CIDADE", ""))).strip(),
            "km": _limpar_km(d.get("km", d.get("KM", 0))),
            "visitado": _para_bool(d.get("visitado", d.get("VISITAMOS", False))),
        } for d in dados]
    else:
        import pandas as pd  # só importa se precisar de planilha
        if ext in (".xlsx", ".xls"):
            df = pd.read_excel(caminho)
        else:  # .csv — tenta utf-8 e cai pra latin1 (comum em CSV brasileiro)
            try:
                df = pd.read_csv(caminho)
            except UnicodeDecodeError:
                df = pd.read_csv(caminho, encoding="latin1")

        col_cidade = _achar_coluna(df.columns, "cidade")
        col_km = _achar_coluna(df.columns, "km")
        col_vis = _achar_coluna(df.columns, "visitamos", "visitado", "visitada")
        if not col_cidade or not col_km:
            raise ValueError("A planilha precisa ter, no mínimo, as colunas CIDADE e KM.")

        lista = []
        for _, linha in df.iterrows():
            nome = str(linha[col_cidade]).strip()
            if not nome or nome.lower() == "nan":
                continue
            lista.append({
                "cidade": nome,
                "km": _limpar_km(linha[col_km]),
                "visitado": _para_bool(linha[col_vis]) if col_vis else False,
            })

    # remove duplicadas (mesmo nome) e ordena por distância
    vistas, unicas = set(), []
    for c in lista:
        chave = c["cidade"].lower()
        if c["cidade"] and chave not in vistas:
            vistas.add(chave)
            unicas.append(c)
    unicas.sort(key=lambda c: c["km"])
    return unicas


# ---------- geração do HTML ----------

def _linha_maps(origem):
    """Monta a linha 'const mapsUrl=...' do HTML.
    origem=None  -> rota sai do GPS do celular (de onde estiverem).
    origem="..." -> rota sai sempre desse lugar."""
    if origem:
        o = json.dumps(str(origem), ensure_ascii=False)
        return ('const mapsUrl=city=>"https://www.google.com/maps/dir/?api=1&origin="'
                '+encodeURIComponent(' + o + ')+"&destination="'
                '+encodeURIComponent(city.cidade+", SP, Brasil");')
    return ('const mapsUrl=city=>"https://www.google.com/maps/dir/?api=1&destination="'
            '+encodeURIComponent(city.cidade+", SP, Brasil");')


def gerar(dados, template="index.html", saida="index.html", origem=None):
    """Injeta a lista 'dados' dentro do HTML modelo, sem tocar no visual."""
    html = Path(template).read_text(encoding="utf-8")
    seed_json = json.dumps(dados, ensure_ascii=False)

    novo, n = re.subn(
        r"const SEED = \[.*?\];",
        "const SEED = " + seed_json + ";",
        html, count=1, flags=re.DOTALL,
    )
    if n == 0:
        raise RuntimeError(
            "Não achei a linha 'const SEED = [...]' no template. "
            "Confirme que o --template aponta pro app correto."
        )

    # reforça o modo da rota (por padrão: sair de onde estiverem)
    novo, _ = re.subn(r"const mapsUrl=city=>[^\n]*?;", _linha_maps(origem), novo, count=1)

    Path(saida).write_text(novo, encoding="utf-8")
    visitadas = sum(c["visitado"] for c in dados)
    rota = f"origem fixa em {origem}" if origem else "de onde vocês estiverem (GPS)"
    print(f"OK! {len(dados)} cidades ({visitadas} visitadas) gravadas em '{saida}'. Rota: {rota}.")


# ---------- linha de comando ----------

if __name__ == "__main__":
    p = argparse.ArgumentParser(
        description='Atualiza a lista de cidades do app "Nossos Passeios".'
    )
    p.add_argument("entrada", nargs="?", default="viagens_atualizado.xlsx",
                   help="planilha .xlsx/.csv ou backup .json (padrão: viagens_atualizado.xlsx)")
    p.add_argument("saida", nargs="?", default="index.html",
                   help="HTML de saída (padrão: index.html)")
    p.add_argument("--template", default="index.html",
                   help="HTML usado como modelo do visual (padrão: index.html)")
    p.add_argument("--origem", default=None,
                   help='fixa a saída da rota (ex.: "Franco da Rocha, SP"). '
                        "Sem isso, a rota sai de onde vocês estiverem (GPS).")
    args = p.parse_args()

    dados = ler_dados(args.entrada)
    gerar(dados, template=args.template, saida=args.saida, origem=args.origem)
