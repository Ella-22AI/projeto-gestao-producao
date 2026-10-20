import sqlite3
from decimal import Decimal, InvalidOperation
from pathlib import Path


DB_PATH = Path(__file__).parent / "database" / "producao_db.db"
SCHEMA_PATH = Path(__file__).parent / "database" / "schema.sql"
MIGRATION_PATH = (
    Path(__file__).parent / "database" / "migrations" / "001_custo_em_centavos.sql"
)
ID_MIGRATION_PATH = (
    Path(__file__).parent / "database" / "migrations" / "002_ids_nao_reutilizaveis.sql"
)


def inicializar_banco(conexao):
    tabela = conexao.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'producao'"
    ).fetchone()
    if not tabela:
        conexao.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        return

    colunas = {
        linha[1]
        for linha in conexao.execute("PRAGMA table_info(producao)").fetchall()
    }
    if "custo_unitario" in colunas and "custo_unitario_centavos" not in colunas:
        conexao.executescript(MIGRATION_PATH.read_text(encoding="utf-8"))
    elif "custo_unitario_centavos" not in colunas:
        raise RuntimeError("O esquema da tabela producao não é reconhecido.")

    definicao = conexao.execute(
        "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = 'producao'"
    ).fetchone()
    if definicao and "AUTOINCREMENT" not in definicao[0].upper():
        conexao.executescript(ID_MIGRATION_PATH.read_text(encoding="utf-8"))


def ler_inteiro(mensagem, minimo=0):
    while True:
        try:
            valor = int(input(mensagem))
            if valor < minimo:
                raise ValueError
            return valor
        except ValueError:
            print(f"Digite um número inteiro maior ou igual a {minimo}.")


def ler_custo(mensagem):
    while True:
        try:
            valor = Decimal(input(mensagem).strip().replace(",", "."))
            if (
                not valor.is_finite()
                or valor < 0
                or valor != valor.quantize(Decimal("0.01"))
            ):
                raise ValueError
            return int(valor * 100)
        except (InvalidOperation, ValueError):
            print("Digite um custo válido, não negativo e com até duas casas decimais.")


def ler_registro():
    setor = input("Setor: ").strip()
    while not setor:
        print("O setor não pode ficar vazio.")
        setor = input("Setor: ").strip()

    pecas_produzidas = ler_inteiro("Peças produzidas no total: ")
    pecas_rejeitadas = ler_inteiro("Peças rejeitadas: ")
    while pecas_rejeitadas > pecas_produzidas:
        print("Peças rejeitadas não podem exceder o total produzido.")
        pecas_rejeitadas = ler_inteiro("Peças rejeitadas: ")
    custo_unitario_centavos = ler_custo("Custo unitário: R$ ")
    return setor, pecas_produzidas, pecas_rejeitadas, custo_unitario_centavos


def formatar_custo(centavos):
    valor = Decimal(centavos) / 100
    return f"R$ {valor:.2f}"


def exibir_registro(registro):
    print(
        f"ID: {registro[0]} | Setor: {registro[1]} | "
        f"Produzidas: {registro[2]} | Rejeitadas: {registro[3]} | "
        f"Custo unitário: {formatar_custo(registro[4])}"
    )


def cadastrar_registro(conexao):
    dados = ler_registro()
    conexao.execute(
        """INSERT INTO producao
              (setor, pecas_produzidas, pecas_rejeitadas, custo_unitario_centavos)
           VALUES (?, ?, ?, ?)""",
        dados,
    )
    conexao.commit()
    print("Registro cadastrado com sucesso.")


def listar_registros(conexao):
    registros = conexao.execute(
        "SELECT id, setor, pecas_produzidas, pecas_rejeitadas, custo_unitario_centavos "
        "FROM producao ORDER BY id"
    ).fetchall()
    if not registros:
        print("Nenhum registro encontrado.")
        return
    for registro in registros:
        exibir_registro(registro)


def consultar_registro(conexao):
    registro_id = ler_inteiro("ID do registro: ", minimo=1)
    registro = conexao.execute(
        "SELECT id, setor, pecas_produzidas, pecas_rejeitadas, custo_unitario_centavos "
        "FROM producao WHERE id = ?",
        (registro_id,),
    ).fetchone()
    if registro:
        exibir_registro(registro)
    else:
        print("Registro não encontrado.")


def atualizar_registro(conexao):
    registro_id = ler_inteiro("ID do registro a atualizar: ", minimo=1)
    registro = conexao.execute(
        "SELECT id FROM producao WHERE id = ?", (registro_id,)
    ).fetchone()
    if not registro:
        print("Registro não encontrado.")
        return

    dados = ler_registro()
    conexao.execute(
        """UPDATE producao
           SET setor = ?, pecas_produzidas = ?, pecas_rejeitadas = ?,
               custo_unitario_centavos = ?
           WHERE id = ?""",
        (*dados, registro_id),
    )
    conexao.commit()
    print("Registro atualizado com sucesso.")


def excluir_registro(conexao):
    registro_id = ler_inteiro("ID do registro a excluir: ", minimo=1)
    registro = conexao.execute(
        "SELECT id FROM producao WHERE id = ?", (registro_id,)
    ).fetchone()
    if not registro:
        print("Registro não encontrado.")
        return

    confirmacao = input("Confirmar exclusão? (s/n): ").strip().lower()
    if confirmacao == "s":
        conexao.execute("DELETE FROM producao WHERE id = ?", (registro_id,))
        conexao.commit()
        print("Registro excluído com sucesso.")
    else:
        print("Exclusão cancelada.")


def exibir_indicadores(conexao):
    total_registros, produzidas, rejeitadas, soma_custos_centavos = conexao.execute(
        """SELECT COUNT(*), COALESCE(SUM(pecas_produzidas), 0),
                  COALESCE(SUM(pecas_rejeitadas), 0),
                  COALESCE(SUM(custo_unitario_centavos), 0)
           FROM producao"""
    ).fetchone()
    pecas_aprovadas = produzidas - rejeitadas
    taxa_rejeicao = rejeitadas / produzidas * 100 if produzidas else 0
    custo_medio_centavos = (
        (soma_custos_centavos + total_registros // 2) // total_registros
        if total_registros
        else 0
    )
    print(f"Registros cadastrados: {total_registros}")
    print(f"Peças produzidas no total: {produzidas}")
    print(f"Peças aprovadas: {pecas_aprovadas}")
    print(f"Peças rejeitadas: {rejeitadas}")
    print(f"Taxa de rejeição: {taxa_rejeicao:.2f}%")
    print(f"Custo unitário médio: {formatar_custo(custo_medio_centavos)}")


def main():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conexao:
        inicializar_banco(conexao)
        while True:
            print("\n----- controle de produção -----")
            print("1. Cadastrar registro")
            print("2. Listar todos os registros")
            print("3. Consultar por ID")
            print("4. Atualizar registro")
            print("5. Excluir registro")
            print("6. Indicadores")
            print("0. Sair")

            opcao = input("Opção: ").strip()
            acoes = {
                "1": cadastrar_registro,
                "2": listar_registros,
                "3": consultar_registro,
                "4": atualizar_registro,
                "5": excluir_registro,
                "6": exibir_indicadores,
            }
            if opcao == "0":
                print("Programa encerrado.")
                break
            acao = acoes.get(opcao)
            if acao:
                acao(conexao)
            else:
                print("Opção inválida. Escolha uma opção de 0 a 6.")


if __name__ == "__main__":
    main()