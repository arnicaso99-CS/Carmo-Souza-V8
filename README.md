# Carmo-Souza V8 Data Converter

Conversor minimo e independente para transformar exportacoes CSV/JSON do simulador Carmo-Souza em um formato normalizado, auditavel e simples.

A pagina Manus publica informa o modelo Carmo-Souza 1D e diz que o simulador exporta dados em CSV/PNG, mas o acesso ao simulador exige login. Por isso, esta alternativa evita depender do Manus: exporte ou cole os dados que voce tiver e rode localmente.

## Caminho mais simples

```bash
python carmo_souza_converter.py entrada.csv -o saida
```

A saida tera:

- `normalized.csv` com colunas `time,x,s`
- `metrics.json` com norma L2, energia funcional aproximada, minimo, maximo, media e variacao total
- `report.md` com um resumo legivel

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
