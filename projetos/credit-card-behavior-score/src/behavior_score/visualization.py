"""Configurações compartilhadas de visualização do projeto."""

from __future__ import annotations

import matplotlib.pyplot as plt


CORES = {
    "principal": "#54B69B",
    "secundaria": "#A7DCDA",
    "lima": "#DDE461",
    "amarelo": "#F4E13D",
    "verde": "#009840",
    "destaque": "#F850D8",
    "preto": "#050708",
    "branco": "#FFFFFF",
    "cinza": "#6B7280",
    "cinza_claro": "#E5E7EB",
}


def definir_estilo_graficos() -> None:
    """Aplica o padrão visual compartilhado aos gráficos do projeto."""

    plt.rcParams.update(
        {
            "figure.figsize": (10, 6),
            "figure.dpi": 120,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.titleweight": "bold",
            "axes.titlesize": 14,
            "axes.labelsize": 11,
            "xtick.labelsize": 10,
            "ytick.labelsize": 10,
            "legend.frameon": False,
            "font.size": 10,
        }
    )


def salvar_figura(figura, caminho: str, dpi: int = 200) -> None:
    """Salva uma figura utilizando o padrão visual do projeto."""

    figura.savefig(
        caminho,
        dpi=dpi,
        bbox_inches="tight",
        facecolor="white",
    )
