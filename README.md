# Carmo-Souza V8 Data Converter

Conversor minimo e independente para transformar exportacoes CSV/JSON do simulador Carmo-Souza em um formato normalizado, auditavel e simples.

A pagina Manus publica informa o modelo Carmo-Souza 1D e diz que o simulador exporta dados em CSV/PNG, mas o acesso ao simulador exige login. Por isso, esta alternativa evita depender do Manus: exporte ou cole os dados que voce tiver e rode localmente.

## Rodar localmente de graca

Nao precisa pagar servidor, API, cloud ou banco de dados. O projeto usa apenas HTML/JavaScript no navegador e Python padrao.

### Opcao 1 - navegador, sem instalar nada alem do download

1. Baixe ou clone este repositorio.
2. Abra `index.html` no navegador.
3. Cole CSV ou JSON.
4. Clique em `Converter`.
5. Baixe `normalized.csv`, `metrics.json` e `report.md`.

### Opcao 2 - servidor local Python

```bash
python run_local.py
```

Depois abra:

```text
http://127.0.0.1:8000/index.html
```

### Opcao 3 - linha de comando

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

## Uso pelo navegador

Abra `index.html` localmente, cole um CSV/JSON e clique em converter. Nenhuma dependencia externa e necessaria.
