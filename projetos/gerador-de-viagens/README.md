# Nossos Passeios 🚂🍊

App simples para sortear o próximo passeio com base em uma lista de cidades, distância máxima e lugares que ainda não foram visitados.

A ideia é ajudar a escolher destinos próximos de forma leve e prática. Você define uma distância máxima, o app filtra apenas as cidades ainda não visitadas e sorteia uma opção. Depois, é possível abrir a rota direto no Google Maps.

## Acesse o app

https://ariel-velardo.github.io/datascience/projetos/gerador-de-viagens/

## Funcionalidades

- Sorteio de cidades ainda não visitadas
- Filtro por distância máxima
- Busca por cidade e filtro de cidades não visitadas
- Visualização do destino sorteado em mapa
- Links de pesquisa de restaurantes para a cidade sorteada
- Cadastro manual de novas cidades pelo próprio app
- Marcação de cidades já visitadas
- Abertura da rota no Google Maps
- Salvamento local no navegador
- Exportação e importação de backup em JSON
- Atualização da lista original a partir de planilha Excel, CSV ou backup JSON

## Como o projeto funciona

O projeto foi desenvolvido como um site estático em HTML, CSS e JavaScript.

O arquivo principal do app é o `index.html`. Ele contém a interface visual, a lógica de sorteio e a lista inicial de cidades.

Para facilitar a manutenção dos dados, existe também o script `gerar_app.py`. Esse script lê uma planilha Excel, um arquivo CSV ou um backup JSON e atualiza automaticamente a lista de cidades dentro do `index.html`.

As alterações feitas dentro do app, como novas cidades e cidades marcadas como visitadas, ficam salvas no navegador do usuário por meio do `localStorage`.

Isso significa que cada pessoa pode usar o app com sua própria lista local, sem precisar de login, servidor ou banco de dados.

## Arquivos do projeto

| Arquivo | Descrição |
| --- | --- |
| `index.html` | Arquivo principal do app |
| `gerar_app.py` | Script que atualiza o HTML com base em uma planilha, CSV ou backup JSON |
| `requirements.txt` | Dependências necessárias para rodar o script Python |
| `.gitignore` | Arquivos e pastas ignorados pelo Git |

## Estrutura esperada da planilha

A planilha deve conter, no mínimo, as colunas abaixo:

| Coluna | Obrigatória | Descrição |
| --- | --- | --- |
| `CIDADE` | Sim | Nome da cidade |
| `KM` | Sim | Distância em quilômetros |
| `VISITAMOS` | Não | Indica se a cidade já foi visitada |

A coluna `VISITAMOS` aceita diferentes formas de preenchimento:

| Situação | Valores aceitos |
| --- | --- |
| Cidade visitada | `S`, `Sim`, `1`, `True`, `x`, `Yes` |
| Cidade não visitada | `N`, `Não`, `0`, `False` ou célula vazia |

Se a coluna `VISITAMOS` não existir, o app considera todas as cidades como não visitadas.

## Como rodar localmente

Clone o repositório:

```bash
git clone https://github.com/ariel-velardo/datascience.git
```

Entre na pasta do projeto:

```bash
cd datascience/projetos/gerador-de-viagens
```

Crie um ambiente virtual:

```bash
python -m venv .venv
```

Ative o ambiente virtual no Windows:

```bash
.venv\Scripts\activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

Abra o arquivo `index.html` no navegador para usar o app localmente.

## Como atualizar a lista de cidades

Para atualizar a lista inicial do app, crie ou edite uma planilha com as colunas `CIDADE`, `KM` e `VISITAMOS`.

Por padrão, o script procura uma planilha chamada:

```text
viagens_atualizado.xlsx
```

Depois rode:

```bash
python gerar_app.py
```

O script vai atualizar o arquivo `index.html` com a nova lista de cidades.

Depois, envie a atualização para o GitHub:

```bash
git add projetos/gerador-de-viagens
git commit -m "Atualiza lista de cidades do app de viagens"
git push origin main
```

## Exemplos de uso do script

Ler a planilha padrão e atualizar o `index.html`:

```bash
python gerar_app.py
```

Ler um arquivo CSV:

```bash
python gerar_app.py minha_lista.csv
```

Gerar um novo HTML a partir de um backup JSON:

```bash
python gerar_app.py backup.json app_novo.html
```

Fixar uma cidade de origem para as rotas:

```bash
python gerar_app.py --origem "Franco da Rocha, SP"
```

Sem o parâmetro `--origem`, o Google Maps calcula a rota a partir da localização atual do usuário.

## Publicação

O app está publicado com GitHub Pages a partir do repositório `datascience`.

URL do projeto:

```text
https://ariel-velardo.github.io/datascience/projetos/gerador-de-viagens/
```

## Observação importante

Esta versão não usa banco de dados.

Cada pessoa que acessa o app consegue cadastrar cidades, marcar visitas e fazer sorteios, mas essas informações ficam salvas apenas no navegador dela.

Para que todos os usuários compartilhem a mesma lista em tempo real, seria necessário evoluir o projeto para uma versão com backend e banco de dados, como Supabase ou Firebase.

## Próximas melhorias possíveis

- Criar login de usuários
- Salvar cidades em banco de dados online
- Compartilhar uma lista única entre várias pessoas
- Adicionar categorias de passeio
- Adicionar imagem ou descrição para cada cidade
- Criar filtros por tipo de passeio
- Melhorar o sorteio com pesos por distância ou prioridade
