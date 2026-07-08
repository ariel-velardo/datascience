# Nossos Passeios 🚂🍊

App simples para sortear o próximo passeio com base em uma lista de cidades, distância máxima e lugares que ainda não foram visitados.

A ideia é ajudar a escolher destinos próximos de forma leve e prática. Você define uma distância máxima, o app filtra apenas as cidades ainda não visitadas e sorteia uma opção. Depois, é possível abrir a rota direto no Google Maps.

## Acesse o app

https://ariel-velardo.github.io/datascience/projetos/gerador-de-viagens/

## Funcionalidades

- Sorteio de cidades ainda não visitadas
- Filtro por distância máxima
- Cadastro manual de novas cidades pelo próprio app
- Marcação de cidades já visitadas
- Abertura da rota no Google Maps
- Salvamento local no navegador
- Exportação e importação de backup em JSON
- Atualização da lista original a partir de planilha Excel

## Como o projeto funciona

O projeto foi desenvolvido como um site estático em HTML, CSS e JavaScript.

A lista inicial de cidades fica dentro do arquivo `index.html`. Para facilitar a manutenção, existe também o script `gerar_app.py`, que lê uma planilha Excel, CSV ou JSON e atualiza automaticamente os dados do app.

As alterações feitas dentro do app, como novas cidades e cidades visitadas, ficam salvas no navegador do usuário por meio do `localStorage`.

## Arquivos do projeto

| Arquivo | Descrição |
| --- | --- |
| `index.html` | Arquivo principal do app |
| `gerar_app.py` | Script que atualiza o HTML com base em uma planilha, CSV ou backup JSON |
| `viagens_atualizado.xlsx` | Planilha com a lista original de cidades |
| `requirements.txt` | Dependências necessárias para rodar o script Python |
| `.gitignore` | Arquivos e pastas ignorados pelo Git |

## Estrutura esperada da planilha

A planilha deve conter, no mínimo, as colunas abaixo:

| Coluna | Obrigatória | Descrição |
| --- | --- | --- |
| `CIDADE` | Sim | Nome da cidade |
| `KM` | Sim | Distância em quilômetros |
| `VISITAMOS` | Não | Indica se a cidade já foi visitada |

A coluna `VISITAMOS` aceita valores como:

```text
S
N
Sim
Não
1
0
True
False