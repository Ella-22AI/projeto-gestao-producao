import contextlib
import io
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import main


class MenuTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_db_path = main.DB_PATH
        main.DB_PATH = Path(self.temp_dir.name) / "producao_db.db"

    def tearDown(self):
        main.DB_PATH = self.original_db_path
        self.temp_dir.cleanup()

    def executar_menu(self, entradas):
        respostas = iter(entradas)
        saida = io.StringIO()
        with patch("builtins.input", side_effect=lambda _: next(respostas)):
            with contextlib.redirect_stdout(saida):
                main.main()
        return saida.getvalue()

    def test_menu_crud_validacoes_e_indicadores(self):
        saida = self.executar_menu([
            "inválida",
            "1", "Montagem", "10", "11", "2", "0,10",
            "2",
            "3", "1",
            "6",
            "4", "1", "Montagem atualizada", "12", "2", "12,50",
            "5", "1", "n",
            "5", "1", "s",
            "2",
            "0",
        ])

        self.assertIn("Opção inválida", saida)
        self.assertIn("Peças rejeitadas não podem exceder", saida)
        self.assertIn("Custo unitário: R$ 0.10", saida)
        self.assertIn("Taxa de rejeição: 20.00%", saida)
        self.assertIn("Custo unitário médio: R$ 0.10", saida)
        self.assertIn("Registro atualizado com sucesso.", saida)
        self.assertIn("Exclusão cancelada.", saida)
        self.assertIn("Registro excluído com sucesso.", saida)
        self.assertIn("Nenhum registro encontrado.", saida)

        with sqlite3.connect(main.DB_PATH) as conexao:
            total = conexao.execute("SELECT COUNT(*) FROM producao").fetchone()[0]
        self.assertEqual(total, 0)

    def test_migra_registros_existentes_preservando_valores(self):
        with sqlite3.connect(main.DB_PATH) as conexao:
            conexao.execute(
                """CREATE TABLE producao (
                    id INTEGER PRIMARY KEY,
                    setor TEXT NOT NULL,
                    pecas_produzidas INTEGER NOT NULL DEFAULT 0,
                    pecas_rejeitadas INTEGER NOT NULL DEFAULT 0,
                    custo_unitario REAL NOT NULL
                )"""
            )
            conexao.execute(
                """INSERT INTO producao VALUES
                   (7, 'Usinagem', 20, 2, 18.75)"""
            )

        saida = self.executar_menu(["0"])

        self.assertIn("Programa encerrado.", saida)
        with sqlite3.connect(main.DB_PATH) as conexao:
            registro = conexao.execute(
                """SELECT id, setor, pecas_produzidas, pecas_rejeitadas,
                          custo_unitario_centavos
                   FROM producao"""
            ).fetchone()
        self.assertEqual(registro, (7, "Usinagem", 20, 2, 1875))


if __name__ == "__main__":
    unittest.main()