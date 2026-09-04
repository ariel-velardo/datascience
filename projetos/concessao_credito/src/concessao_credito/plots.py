import plotly.io as pio
import plotly.graph_objects as go


CORES = {
    "verde_escuro": "#1B5C0B",
    "verde_principal": "#2E7D18",
    "verde_vivo": "#64BE28",
    "verde_medio": "#0B7D35",
    "verde_claro": "#EAF6E6",
    "cinza_texto": "#2F3D32",
    "cinza_medio": "#6B756B",
    "cinza_claro": "#F4F6F3",
    "amarelo": "#F2C400",
    "marrom": "#6B421F",
    "branco": "#FFFFFF",
}


PALETA_RISCO = {
    "baixo": CORES["verde_vivo"],
    "medio": CORES["amarelo"],
    "alto": CORES["marrom"],
    "muito_alto": CORES["verde_escuro"],
}


def registrar_template_credito():
    """
    Registra um template Plotly com identidade visual verde,
    sem uso de marca ou logotipo.
    """
    template = go.layout.Template(
        layout=go.Layout(
            font=dict(
                family="Arial",
                color=CORES["cinza_texto"],
                size=14,
            ),
            title=dict(
                font=dict(size=22, color=CORES["cinza_texto"]),
                x=0.02,
                xanchor="left",
            ),
            paper_bgcolor=CORES["branco"],
            plot_bgcolor=CORES["branco"],
            colorway=[
                CORES["verde_principal"],
                CORES["verde_vivo"],
                CORES["verde_medio"],
                CORES["amarelo"],
                CORES["marrom"],
                CORES["cinza_medio"],
            ],
            margin=dict(l=70, r=40, t=80, b=60),
            legend=dict(
                bgcolor="rgba(255,255,255,0)",
                font=dict(color=CORES["cinza_texto"]),
            ),
        )
    )

    pio.templates["credito_verde"] = template
    pio.templates.default = "credito_verde"


def aplicar_layout(
    fig,
    titulo=None,
    subtitulo=None,
    altura=520,
    largura=None,
    mostrar_legenda=True,
):
    """
    Aplica layout padronizado aos graficos Plotly.
    """
    if titulo and subtitulo:
        titulo_final = f"{titulo}<br><sup>{subtitulo}</sup>"
    else:
        titulo_final = titulo

    fig.update_layout(
        title=titulo_final,
        height=altura,
        width=largura,
        showlegend=mostrar_legenda,
        hovermode="x unified",
    )

    fig.update_xaxes(
        showgrid=False,
        zeroline=False,
        linecolor="#D9DED8",
        tickfont=dict(color=CORES["cinza_texto"]),
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor="#E6EAE5",
        zeroline=False,
        linecolor="#D9DED8",
        tickfont=dict(color=CORES["cinza_texto"]),
    )

    return fig


def salvar_figura(fig, caminho_html=None, caminho_png=None):
    """
    Salva figura Plotly em HTML e/ou PNG.
    Para PNG, requer kaleido instalado.
    """
    if caminho_html:
        fig.write_html(caminho_html)

    if caminho_png:
        fig.write_image(caminho_png, scale=2)