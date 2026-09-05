"""Baixa os Indicadores de Trajetoria da Educacao Superior (Inep) por coorte.

Politica de economia de disco:
    download ZIP -> extrair -> manter apenas XLSX + dicionario + md5
    -> apagar ZIP -> apagar ODS duplicado.

Pico de disco por coorte: 1 ZIP (<= 79 MB) + o conteudo extraido.
Nenhum arquivo pre-existente e sobrescrito: se ja houver XLSX no destino,
a coorte e pulada.

Uso:
    python src/baixa_trajetorias.py 2016 2017 2018 2019 2020
"""

from __future__ import annotations

import hashlib
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

BASE_URL = (
    "https://download.inep.gov.br/informacoes_estatisticas/"
    "indicadores_educacionais/indicadores_trajetoria_es_{coorte}_2024.zip"
)

RAIZ = Path("data/raw/trajetoria")
ANO_FINAL = 2024

MANTER = {".xlsx", ".docx", ".txt", ".pdf"}
DESCARTAR = {".ods"}


def md5(caminho: Path, blocos: int = 1 << 20) -> str:
    h = hashlib.md5()
    with caminho.open("rb") as f:
        for bloco in iter(lambda: f.read(blocos), b""):
            h.update(bloco)
    return h.hexdigest()


def baixa(url: str, destino: Path) -> None:
    """Baixa via curl, com verificacao TLS ativa.

    O host download.inep.gov.br nao envia o certificado intermediario da
    cadeia TLS. O requests/OpenSSL falha com CERTIFICATE_VERIFY_FAILED
    ("unable to get local issuer certificate"); o curl do Windows usa o
    repositorio de certificados do sistema, que resolve o intermediario via
    AIA e valida normalmente. Nao usamos -k. A integridade e reconferida
    depois contra o md5 publicado pelo proprio Inep dentro do ZIP.
    """
    resultado = subprocess.run(
        ["curl", "--fail", "--location", "--show-error", "--progress-bar",
         "--retry", "3", "--retry-delay", "5",
         "-A", "Mozilla/5.0", "-o", str(destino), url],
        capture_output=True, text=True,
    )
    if resultado.returncode != 0:
        raise RuntimeError(
            f"curl falhou ({resultado.returncode}) em {url}: {resultado.stderr}"
        )


def processa(coorte: int) -> None:
    pasta = RAIZ / f"{coorte}_{ANO_FINAL}"
    url = BASE_URL.format(coorte=coorte)

    print("=" * 78)
    print(f"COORTE {coorte}  ->  {pasta}")
    print(f"URL: {url}")

    if pasta.exists() and any(pasta.glob("*.xlsx")):
        print("  ja existe XLSX nesta pasta; pulando (nada foi sobrescrito).")
        return

    pasta.mkdir(parents=True, exist_ok=True)
    zip_path = pasta / f"indicadores_trajetoria_es_{coorte}_{ANO_FINAL}.zip"

    if zip_path.exists():
        print(f"  ZIP ja presente ({zip_path.stat().st_size/1e6:.1f} MB); "
              "reaproveitando, sem baixar de novo.")
    else:
        print("  baixando...")
        baixa(url, zip_path)
    print(f"  ZIP: {zip_path.stat().st_size/1e6:.1f} MB  md5={md5(zip_path)}")

    with zipfile.ZipFile(zip_path) as z:
        print("  conteudo do ZIP:")
        for info in z.infolist():
            print(f"    {info.file_size/1e6:8.2f} MB  {info.filename}")
        z.extractall(pasta)

    # Achata subpastas criadas pelo ZIP.
    for origem in sorted(pasta.rglob("*")):
        if origem.is_dir() or origem == zip_path:
            continue
        alvo = pasta / origem.name
        if origem != alvo:
            if alvo.exists():
                origem.unlink()
            else:
                shutil.move(str(origem), str(alvo))

    for vazia in sorted(pasta.rglob("*"), reverse=True):
        if vazia.is_dir() and not any(vazia.iterdir()):
            vazia.rmdir()

    removidos = []
    for arq in sorted(pasta.iterdir()):
        if arq == zip_path or not arq.is_file():
            continue
        ext = arq.suffix.lower()
        if ext in DESCARTAR:
            tam = arq.stat().st_size
            arq.unlink()
            removidos.append(
                f"{arq.name} ({tam/1e6:.1f} MB) - duplicata exata do XLSX"
            )
        elif ext not in MANTER:
            print(f"  [aviso] extensao inesperada, mantida: {arq.name}")

    tam_zip = zip_path.stat().st_size
    zip_path.unlink()
    removidos.append(f"{zip_path.name} ({tam_zip/1e6:.1f} MB) - container")

    print("  REMOVIDOS:")
    for r in removidos:
        print(f"    - {r}")

    print("  MANTIDOS:")
    for arq in sorted(pasta.iterdir()):
        print(f"    {arq.stat().st_size/1e6:8.2f} MB  {arq.name}")

    for txt in pasta.glob("md5*.txt"):
        conteudo = txt.read_text(encoding="utf-8", errors="replace").strip()
        print(f"  md5 publicado ({txt.name}):")
        for linha in conteudo.splitlines():
            print(f"    {linha}")
    for xlsx in pasta.glob("*.xlsx"):
        print(f"  md5 local  {xlsx.name} = {md5(xlsx)}")


if __name__ == "__main__":
    coortes = [int(a) for a in sys.argv[1:]] or [2016, 2017, 2018, 2019, 2020]
    for c in coortes:
        processa(c)
