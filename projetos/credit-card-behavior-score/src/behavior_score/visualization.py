"""Padrão visual compartilhado dos gráficos do projeto."""

from __future__ import annotations

from pathlib import Path
import warnings

import plotly.graph_objects as go
import plotly.io as pio


CORES = {
    "principal": "#54B69B",
    "secundaria": "#A7DCDA",
    "lima": "#DDE461",
    "amarelo": "#F4E13D",
    "verde": "#009840",
    "destaque": "#F850D8",
    "preto": "#111111",
    "cinza_escuro": "#4B5563",
    "cinza": "#9CA3AF",
    "cinza_claro": "#E5E7EB",
    "fundo": "#FFFFFF",
}


PALETA_CATEGORICA = [
    CORES["principal"],
    CORES["secundaria"],
    CORES["amarelo"],
    CORES["lima"],
    CORES["destaque"],
    CORES["verde"],
]


def configurar_tema_plotly() -> None:
    """Registra e ativa o tema visual padrão do projeto."""

    tema = go.layout.Template()

    tema.layout = go.Layout(
        font=dict(
            family="Segoe UI, Arial, sans-serif",
            size=13,
            color=CORES["preto"],
        ),
        paper_bgcolor=CORES["fundo"],
        plot_bgcolor=CORES["fundo"],
        colorway=PALETA_CATEGORICA,
        title=dict(
            x=0,
            xanchor="left",
            font=dict(
                size=22,
                color=CORES["preto"],
            ),
        ),
        margin=dict(
            l=70,
            r=40,
            t=90,
            b=65,
        ),
        hoverlabel=dict(
            bgcolor=CORES["fundo"],
            font=dict(
                family="Segoe UI, Arial, sans-serif",
                size=12,
                color=CORES["preto"],
            ),
        ),
        legend=dict(
            title=None,
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
        ),
        xaxis=dict(
            showline=False,
            showgrid=False,
            zeroline=False,
            title_font=dict(size=13),
            tickfont=dict(size=12),
        ),
        yaxis=dict(
            showline=False,
            gridcolor=CORES["cinza_claro"],
            gridwidth=1,
            zeroline=False,
            title_font=dict(size=13),
            tickfont=dict(size=12),
        ),
    )

    pio.templates["behavior_score"] = tema
    pio.templates.default = "behavior_score"


def aplicar_layout_executivo(
    figura: go.Figure,
    titulo: str,
    subtitulo: str | None = None,
    titulo_eixo_x: str | None = None,
    titulo_eixo_y: str | None = None,
    altura: int = 550,
    largura: int = 1000,
    mostrar_legenda: bool = True,
) -> go.Figure:
    """Aplica o padrão executivo de apresentação a uma figura Plotly."""

    texto_titulo = titulo

    if subtitulo:
        texto_titulo += (
            f"<br><sup style='color:{CORES['cinza_escuro']}'>"
            f"{subtitulo}</sup>"
        )

    figura.update_layout(
        template="behavior_score",
        title=texto_titulo,
        xaxis_title=titulo_eixo_x,
        yaxis_title=titulo_eixo_y,
        height=altura,
        width=largura,
        showlegend=mostrar_legenda,
        hovermode="closest",
    )

    return figura


def aplicar_eixo_percentual(
    figura: go.Figure,
    eixo: str = "y",
    casas_decimais: int = 1,
) -> go.Figure:
    """Formata um eixo que contém proporções entre zero e um."""

    formato = f".{casas_decimais}%"

    if eixo == "x":
        figura.update_xaxes(tickformat=formato)
    elif eixo == "y":
        figura.update_yaxes(tickformat=formato)
    else:
        raise ValueError("O parâmetro 'eixo' deve ser 'x' ou 'y'.")

    return figura


def salvar_grafico(
    figura: go.Figure,
    nome_arquivo: str,
    pasta: str | Path,
    salvar_html: bool = True,
    salvar_png: bool = True,
    escala_png: int = 2,
) -> None:
    """Salva o gráfico em HTML interativo e PNG para uso executivo."""

    pasta = Path(pasta)
    pasta.mkdir(parents=True, exist_ok=True)

    nome_base = Path(nome_arquivo).stem

    if salvar_html:
        caminho_html = pasta / f"{nome_base}.html"

        figura.write_html(
            caminho_html,
            include_plotlyjs="cdn",
        )

    if salvar_png:
        caminho_png = pasta / f"{nome_base}.png"

        try:
            figura.write_image(
                caminho_png,
                scale=escala_png,
            )
        except Exception as erro:
            warnings.warn(
                "Não foi possível exportar o gráfico para PNG. "
                "O arquivo HTML foi preservado. "
                f"Detalhe: {erro}",
                RuntimeWarning,
            )


configurar_tema_plotly()
