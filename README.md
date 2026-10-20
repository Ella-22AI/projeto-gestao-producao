# Controle de Produção

Aplicação de linha de comando para registrar dados de produção e acompanhar
indicadores operacionais. O projeto combina operações CRUD, validação de dados
e persistência local em SQLite em uma solução leve, desenvolvida com recursos
nativos do Python.

## Visão geral

O sistema organiza informações por setor, permitindo registrar o volume
produzido, as peças rejeitadas e o custo unitário. A partir desses dados, é
possível consultar registros e visualizar indicadores consolidados para apoiar
o acompanhamento da produção.

### Funcionalidades

- Cadastrar, listar e consultar registros por ID.
- Atualizar e excluir registros com confirmação.
- Exibir total produzido, peças aprovadas e rejeitadas, taxa de rejeição e
  custo unitário médio.
- Validar entradas para evitar setores vazios, valores negativos e quantidade
  de rejeições superior à produção.
- Criar o banco SQLite automaticamente na primeira execução.
- Migrar bancos de versões anteriores, preservando os registros existentes.

## Tecnologias e práticas

- **Python 3.10+** — lógica da aplicação e interface interativa no terminal.
- **SQLite** — armazenamento local sem necessidade de servidor.
- **`Decimal` e valores inteiros em centavos** — tratamento de custos sem
  imprecisões comuns de ponto flutuante.
- **`unittest`** — testes automatizados dos fluxos principais e das migrações.
- **Consultas parametrizadas** — interação com o banco usando parâmetros SQL.

## Regras de negócio

- A quantidade produzida inclui as peças rejeitadas.
- Peças aprovadas são calculadas como `produzidas - rejeitadas`.
- A taxa de rejeição é `rejeitadas / produzidas × 100`; quando não há produção,
  a taxa exibida é zero.
- O custo unitário aceita valores não negativos com até duas casas decimais e é
  armazenado na coluna `custo_unitario_centavos`.
- A edição preserva o ID do registro. IDs excluídos não são reutilizados.

## Como executar

Requisito: Python 3.10 ou superior. Não há dependências externas.

```bash
git clone https://github.com/Ella-22AI/projeto-gestao-producao.git
cd projeto-gestao-producao
python main.py
```

Na primeira execução, o programa cria o arquivo `database/producao_db.db` e
inicializa a estrutura necessária. O menu interativo apresenta as opções de
cadastro, consulta, manutenção e indicadores.

## Exemplo de uso

```text
----- controle de produção -----
1. Cadastrar registro
2. Listar todos os registros
3. Consultar por ID
4. Atualizar registro
5. Excluir registro
6. Indicadores
0. Sair
```

Um registro contém setor, quantidade produzida, quantidade rejeitada e custo
unitário. Na listagem, os dados são apresentados com o ID e o custo formatado
em reais.

## Banco de dados e migrações

O esquema atual está definido em [`database/schema.sql`](./database/schema.sql).
Ao iniciar, a aplicação identifica bancos antigos e executa as migrações
necessárias:

- [`001_custo_em_centavos.sql`](./database/migrations/001_custo_em_centavos.sql)
  converte o custo legado para centavos inteiros.
- [`002_ids_nao_reutilizaveis.sql`](./database/migrations/002_ids_nao_reutilizaveis.sql)
  atualiza a tabela para impedir a reutilização de IDs excluídos.

As migrações preservam os dados existentes.

## Testes

Execute a suíte automatizada na raiz do projeto:

```bash
python -m unittest discover -s tests -v
```

Os testes cobrem validações, operações pelo menu, indicadores, preservação da
identidade dos registros e migração de bancos existentes.

## Estrutura do projeto

```text
.
├── main.py
├── database/
│   ├── schema.sql
│   └── migrations/
├── tests/
│   └── test_main.py
└── README.md
```

## Sobre o projeto

Projeto de portfólio que demonstra construção de uma aplicação funcional de
ponta a ponta: modelagem simples de dados, persistência relacional, validação
de regras de negócio, evolução de esquema com migrações e testes automatizados.
