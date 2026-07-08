# Nossos Passeios 🚂🍊

App de bolso pra sortear o próximo passeio do casal. Escolhe uma cidade que
vocês ainda não visitaram, dentro da distância que você quiser, e abre a rota
no Google Maps. Roda no celular como se fosse um aplicativo — é um único
arquivo HTML, sem servidor e sem custo.

O tema visual é inspirado numa estética de animação stop-motion antiga
(vermelho, marrom, verde-musgo, creme e brass).

---

## Arquivos do projeto

| Arquivo                    | Pra que serve                                                        |
|----------------------------|----------------------------------------------------------------------|
| `index.html`               | O app em si. É o que abre no navegador/celular.                      |
| `gerar_app.py`             | Regenera o `index.html` a partir da planilha (só troca os dados).   |
| `viagens_atualizado.xlsx`  | Sua lista de cidades (colunas: CIDADE, KM, VISITAMOS).              |
| `requirements.txt`         | Bibliotecas Python necessárias.                                     |

**Divisão importante:** os **dados** (as cidades) você edita na planilha e roda
o script; o **visual** (cores, textos) você edita direto no `index.html`.

---

## Como rodar no VS Code (Windows)

1. **Python instalado?** No terminal, `python --version`. Se não tiver, instale
   de [python.org](https://www.python.org) marcando *"Add Python to PATH"*.
2. Abra **esta pasta** no VS Code (`File → Open Folder`).
3. Instale a extensão **Python** (da Microsoft), se ainda não tiver.
4. Abra o terminal integrado (`Terminal → New Terminal`).
5. Instale as bibliotecas (uma vez só):
   ```
   pip install -r requirements.txt
   ```

---

## O dia a dia

1. Edite a planilha `viagens_atualizado.xlsx` (adicione cidades, marque as
   visitadas com `S`).
2. No terminal, rode:
   ```
   python gerar_app.py
   ```
3. Pronto: o `index.html` foi atualizado. Mande pro celular e abra no navegador.

### Variações úteis

```
python gerar_app.py minha_lista.csv          # ler de um CSV
python gerar_app.py backup.json app.html     # partir de um backup do app
python gerar_app.py --origem "Franco da Rocha, SP"   # rota sempre saindo de casa
```

Sem `--origem`, a rota sai de onde vocês estiverem (usa o GPS do celular).

---

## Colunas aceitas na planilha

Maiúsculas/minúsculas tanto faz.

- **CIDADE** (ou `cidade`) — nome da cidade *(obrigatório)*
- **KM** (ou `km`) — distância em km, aceita vírgula ou ponto *(obrigatório)*
- **VISITAMOS** (ou `visitado`) — `S/N`, `Sim/Não`, `1/0` ou `True/False` *(opcional)*

---

## Salvar no celular como "app"

Abra o `index.html` no navegador do celular e:

- **iPhone (Safari):** Compartilhar → *Adicionar à Tela de Início*.
- **Android (Chrome):** menu ⋮ → *Adicionar à tela inicial*.

Aí ele vira um ícone e abre em tela cheia. O progresso ("já fomos") fica salvo
no próprio celular; use os botões **Salvar/Restaurar backup** dentro do app pra
guardar uma cópia ou passar a lista pra outro celular.
