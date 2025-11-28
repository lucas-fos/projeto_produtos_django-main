#!/usr/bin/env python3
# biblioteca.py
"""
Sistema simples de biblioteca com persistência SQLite.
Funcionalidades:
- cadastrar livro
- listar livros
- buscar (título/autor)
- emprestar / devolver
- remover livro
"""

import sqlite3
from dataclasses import dataclass, asdict
from typing import Optional, List


DB_PATH = "biblioteca.db"


@dataclass
class Livro:
    id: Optional[int] = None
    titulo: str = ""
    autor: str = ""
    ano: Optional[int] = None
    quantidade: int = 1

    @classmethod
    def from_row(cls, row):
        if row is None:
            return None
        return cls(id=row[0], titulo=row[1], autor=row[2], ano=row[3], quantidade=row[4])


class RepositorioLivros:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._criar_tabela()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _criar_tabela(self):
        sql = """
        CREATE TABLE IF NOT EXISTS livros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            autor TEXT NOT NULL,
            ano INTEGER,
            quantidade INTEGER NOT NULL DEFAULT 1
        );
        """
        with self._connect() as conn:
            conn.execute(sql)
            conn.commit()

    def adicionar(self, livro: Livro) -> Livro:
        sql = "INSERT INTO livros (titulo, autor, ano, quantidade) VALUES (?, ?, ?, ?)"
        with self._connect() as conn:
            cur = conn.execute(sql, (livro.titulo, livro.autor, livro.ano, livro.quantidade))
            livro.id = cur.lastrowid
            conn.commit()
        return livro

    def atualizar(self, livro: Livro) -> None:
        sql = "UPDATE livros SET titulo=?, autor=?, ano=?, quantidade=? WHERE id=?"
        with self._connect() as conn:
            conn.execute(sql, (livro.titulo, livro.autor, livro.ano, livro.quantidade, livro.id))
            conn.commit()

    def remover(self, livro_id: int) -> bool:
        sql = "DELETE FROM livros WHERE id=?"
        with self._connect() as conn:
            cur = conn.execute(sql, (livro_id,))
            conn.commit()
            return cur.rowcount > 0

    def listar_todos(self) -> List[Livro]:
        sql = "SELECT id, titulo, autor, ano, quantidade FROM livros ORDER BY titulo COLLATE NOCASE"
        with self._connect() as conn:
            rows = conn.execute(sql).fetchall()
        return [Livro.from_row(r) for r in rows]

    def buscar(self, termo: str) -> List[Livro]:
        termo_like = f"%{termo}%"
        sql = "SELECT id, titulo, autor, ano, quantidade FROM livros WHERE titulo LIKE ? OR autor LIKE ? ORDER BY titulo COLLATE NOCASE"
        with self._connect() as conn:
            rows = conn.execute(sql, (termo_like, termo_like)).fetchall()
        return [Livro.from_row(r) for r in rows]

    def obter_por_id(self, livro_id: int) -> Optional[Livro]:
        sql = "SELECT id, titulo, autor, ano, quantidade FROM livros WHERE id=?"
        with self._connect() as conn:
            row = conn.execute(sql, (livro_id,)).fetchone()
        return Livro.from_row(row)


class BibliotecaApp:
    def __init__(self):
        self.repo = RepositorioLivros()

    def cadastrar_livro(self):
        print("\n--- Cadastrar Livro ---")
        titulo = input("Título: ").strip()
        autor = input("Autor: ").strip()
        ano_raw = input("Ano (opcional): ").strip()
        ano = int(ano_raw) if ano_raw.isdigit() else None
        qtd_raw = input("Quantidade (padrão 1): ").strip()
        quantidade = int(qtd_raw) if qtd_raw.isdigit() and int(qtd_raw) > 0 else 1

        livro = Livro(titulo=titulo, autor=autor, ano=ano, quantidade=quantidade)
        livro = self.repo.adicionar(livro)
        print(f"Livro cadastrado com ID {livro.id}.\n")

    def listar_livros(self):
        print("\n--- Lista de Livros ---")
        livros = self.repo.listar_todos()
        if not livros:
            print("Nenhum livro cadastrado.\n")
            return
        for l in livros:
            ano = f"{l.ano}" if l.ano is not None else "s/d"
            print(f"[{l.id}] {l.titulo} — {l.autor} ({ano}) | Disponível: {l.quantidade}")
        print("")

    def buscar_livro(self):
        termo = input("\nDigite título ou autor para buscar: ").strip()
        if not termo:
            print("Termo vazio.\n")
            return
        encontrados = self.repo.buscar(termo)
        if not encontrados:
            print("Nenhum resultado encontrado.\n")
            return
        print(f"\nResultados para '{termo}':")
        for l in encontrados:
            ano = f"{l.ano}" if l.ano is not None else "s/d"
            print(f"[{l.id}] {l.titulo} — {l.autor} ({ano}) | Disponível: {l.quantidade}")
        print("")

    def remover_livro(self):
        try:
            livro_id = int(input("\nID do livro a remover: "))
        except ValueError:
            print("ID inválido.\n")
            return
        ok = self.repo.remover(livro_id)
        if ok:
            print("Livro removido com sucesso.\n")
        else:
            print("Livro não encontrado.\n")

    def emprestar(self):
        try:
            livro_id = int(input("\nID do livro para emprestar: "))
        except ValueError:
            print("ID inválido.\n")
            return
        livro = self.repo.obter_por_id(livro_id)
        if not livro:
            print("Livro não encontrado.\n")
            return
        if livro.quantidade <= 0:
            print("Nenhuma cópia disponível para empréstimo.\n")
            return
        livro.quantidade -= 1
        self.repo.atualizar(livro)
        print(f"Livro '{livro.titulo}' emprestado. Restam {livro.quantidade} cópias.\n")

    def devolver(self):
        try:
            livro_id = int(input("\nID do livro para devolver: "))
        except ValueError:
            print("ID inválido.\n")
            return
        livro = self.repo.obter_por_id(livro_id)
        if not livro:
            print("Livro não encontrado.\n")
            return
        livro.quantidade += 1
        self.repo.atualizar(livro)
        print(f"Livro '{livro.titulo}' devolvido. Disponível: {livro.quantidade} cópias.\n")

    def editar_livro(self):
        try:
            livro_id = int(input("\nID do livro para editar: "))
        except ValueError:
            print("ID inválido.\n")
            return
        livro = self.repo.obter_por_id(livro_id)
        if not livro:
            print("Livro não encontrado.\n")
            return
        print("Deixe em branco para manter o valor atual.")
        titulo = input(f"Título [{livro.titulo}]: ").strip() or livro.titulo
        autor = input(f"Autor [{livro.autor}]: ").strip() or livro.autor
        ano_raw = input(f"Ano [{livro.ano if livro.ano else 's/d'}]: ").strip()
        ano = int(ano_raw) if ano_raw.isdigit() else livro.ano
        qtd_raw = input(f"Quantidade [{livro.quantidade}]: ").strip()
        quantidade = int(qtd_raw) if qtd_raw.isdigit() else livro.quantidade

        livro.titulo = titulo
        livro.autor = autor
        livro.ano = ano
        livro.quantidade = quantidade
        self.repo.atualizar(livro)
        print("Livro atualizado.\n")

    def menu(self):
        while True:
            print("=== Sistema de Biblioteca ===")
            print("1 - Cadastrar livro")
            print("2 - Listar livros")
            print("3 - Buscar livro")
            print("4 - Editar livro")
            print("5 - Remover livro")
            print("6 - Emprestar livro")
            print("7 - Devolver livro")
            print("0 - Sair")
            opc = input("Escolha uma opção: ").strip()
            if opc == "1":
                self.cadastrar_livro()
            elif opc == "2":
                self.listar_livros()
            elif opc == "3":
                self.buscar_livro()
            elif opc == "4":
                self.editar_livro()
            elif opc == "5":
                self.remover_livro()
            elif opc == "6":
                self.emprestar()
            elif opc == "7":
                self.devolver()
            elif opc == "0":
                print("Saindo... Até mais!")
                break
            else:
                print("Opção inválida. Tente novamente.\n")


if __name__ == "__main__":
    app = BibliotecaApp()
    app.menu()