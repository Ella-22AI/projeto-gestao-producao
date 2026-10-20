# projeto-gestao-producao

Aplicação de linha de comando para cadastrar e acompanhar registros de produção
em um banco SQLite.

## Executar

Use Python 3.10 ou superior, sem dependências externas:

```bash
python main.py
```

O banco `database/producao_db.db` é criado automaticamente. O menu permite
cadastrar, listar, consultar, atualizar e excluir registros, além de exibir
indicadores agregados.

## Dados

`pecas_produzidas` representa o total produzido, incluindo as peças rejeitadas.
Assim, `pecas_rejeitadas` não pode ser maior que `pecas_produzidas`, e a taxa de
rejeição é calculada como rejeitadas / total produzido. O número de peças
aprovadas é o total produzido menos as rejeitadas.

Os custos são armazenados como inteiros em centavos na coluna
`custo_unitario_centavos`, evitando imprecisões de ponto flutuante. Ao abrir um
banco criado pela versão anterior, o programa migra os valores existentes de
`custo_unitario` automaticamente, preservando os registros. O esquema atual
está em `database/schema.sql`.

## Testes

Execute a suíte com:

```bash
python -m unittest discover -s tests -v
```