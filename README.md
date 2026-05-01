# Carmo-Souza V8 Web Converter

Conversor web minimo e independente para transformar exportacoes CSV/JSON do simulador Carmo-Souza em um formato normalizado, auditavel e simples.

## Rodar na web de graca

Este repositorio esta preparado para GitHub Pages via GitHub Actions.

URL esperada depois do deploy:

```text
https://arnicaso99-cs.github.io/Carmo-Souza-V8/
```

Se a URL ainda nao abrir, ative uma vez no GitHub:

1. Abra o repositorio `arnicaso99-CS/Carmo-Souza-V8`.
2. Va em `Settings` > `Pages`.
3. Em `Build and deployment`, selecione `Source: GitHub Actions`.
4. Volte em `Actions` e rode `Deploy web app to GitHub Pages`, ou faca qualquer commit na branch `main`.

Depois disso, o site fica online de graca e atualiza automaticamente a cada push na `main`.

## Como usar no site

1. Abra a URL do GitHub Pages.
2. Cole CSV ou JSON no campo principal.
3. Clique em `Converter`.
4. Baixe `normalized.csv`, `metrics.json` e `report.md`.

Tudo roda no navegador. Os dados nao precisam sair do computador do usuario.

## Rodar localmente tambem

Nao precisa pagar servidor, API, cloud ou banco de dados. O projeto usa apenas HTML/JavaScript no navegador e Python padrao.

### Navegador local

1. Baixe ou clone este repositorio.
2. Abra `index.html` no navegador.
3. Cole CSV ou JSON.
4. Clique em `Converter`.

### Servidor local Python

```bash
python run_local.py
```

Depois abra:

```text
http://127.0.0.1:8000/index.html
```

### Linha de comando

```bash
python carmo_souza_converter.py sample_data/example.csv -o saida
```

A saida tera:

- `saida/normalized.csv` com colunas `time,x,s`
- `saida/metrics.json` com norma L2, energia funcional aproximada, minimo, maximo, media e variacao total
- `saida/report.md` com um resumo legivel

## Conectar pelo GitHub

```bash
git clone https://github.com/arnicaso99-CS/Carmo-Souza-V8.git
cd Carmo-Souza-V8
python run_local.py
```

Para atualizar depois:

```bash
git pull
```

## Formatos aceitos

O conversor aceita:

1. CSV com cabecalho, por exemplo:

```csv
time,x,s
0,0,0.1
0,1,0.2
1,0,0.15
1,1,0.18
```

2. CSV sem cabecalho, como vetor ou matriz numerica.
3. JSON contendo lista de registros ou campos como `data`, `rows`, `records`, `points`, `history`, `simulations`, `result` ou `results`.

## Esquema de saida

```csv
time,x,s
0.0,0.0,0.1
0.0,1.0,0.2
```

## Parametros opcionais

```bash
python carmo_souza_converter.py entrada.csv -o saida --alpha 1 --beta 1 --delta 1
```

Esses parametros entram apenas no calculo aproximado da energia funcional.

## Observacao epistemologica

A saida e marcada como `E8 - Resultado computacional`. Isso significa que ela organiza e audita os dados, mas nao substitui validacao matematica, experimental ou revisao externa.
