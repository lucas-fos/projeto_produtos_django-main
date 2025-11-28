#!/usr/bin/env python3
# usuario.py
"""
Sistema simples de biblioteca com persistência SQLite.
Funcionalidades:
- cadastrar usuário
- listar usuários
- buscar (título/autor)
- emprestar / devolver
- remover usuário
"""

import sqlite3
from dataclasses import dataclass, asdict
from typing import Optional, List


DB_PATH = "biblioteca.db"


@dataclass
class Usuario:
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


class RepositorioUsuarios:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._criar_tabela()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _criar_tabela(self):
        sql = """
        CREATE TABLE IF NOT EXISTS usuarios (
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

    def adicionar(self, usuario: Usuario) -> Usuario:
        sql = "INSERT INTO usuarios (titulo, autor, ano, quantidade) VALUES (?, ?, ?, ?)"
        with self._connect() as conn:
            cur = conn.execute(sql, (usuario.titulo, usuario.autor, usuario.ano, usuario.quantidade))
            usuario.id = cur.lastrowid
            conn.commit()
        return usuario

    def atualizar(self, usuario: Usuario) -> None:
        sql = "UPDATE usuarios SET titulo=?, autor=?, ano=?, quantidade=? WHERE id=?"
        with self._connect() as conn:
            conn.execute(sql, (usuario.titulo, usuario.autor, usuario.ano, usuario.quantidade, usuario.id))
            conn.commit()

    def remover(self, usuario_id: int) -> bool:
        sql = "DELETE FROM usuarios WHERE id=?"
        with self._connect() as conn:
            cur = conn.execute(sql, (usuario_id,))
            conn.commit()
            return cur.rowcount > 0

    def listar_todos(self) -> List[Usuario]:
        sql = "SELECT id, titulo, autor, ano, quantidade FROM usuarios ORDER BY titulo COLLATE NOCASE"
        with self._connect() as conn:
            rows = conn.execute(sql).fetchall()
        return [Usuario.from_row(r) for r in rows]

    def buscar(self, termo: str) -> List[Usuario]:
        termo_like = f"%{termo}%"
        sql = "SELECT id, titulo, autor, ano, quantidade FROM usuarios WHERE titulo LIKE ? OR autor LIKE ? ORDER BY titulo COLLATE NOCASE"
        with self._connect() as conn:
            rows = conn.execute(sql, (termo_like, termo_like)).fetchall()
        return [Usuario.from_row(r) for r in rows]

    def obter_por_id(self, usuario_id: int) -> Optional[Usuario]:
        sql = "SELECT id, titulo, autor, ano, quantidade FROM usuarios WHERE id=?"
        with self._connect() as conn:
            row = conn.execute(sql, (usuario_id,)).fetchone()
        return Usuario.from_row(row)


class BibliotecaApp:
    def __init__(self):
        self.repo = RepositorioUsuarios()

    def cadastrar_usuario(self):
        print("\n--- Cadastrar Usuário ---")
        titulo = input("Título: ").strip()
        autor = input("Autor: ").strip()
        ano_raw = input("Ano (opcional): ").strip()
        ano = int(ano_raw) if ano_raw.isdigit() else None
        qtd_raw = input("Quantidade (padrão 1): ").strip()
        quantidade = int(qtd_raw) if qtd_raw.isdigit() and int(qtd_raw) > 0 else 1

        usuario = Usuario(titulo=titulo, autor=autor, ano=ano, quantidade=quantidade)
        usuario = self.repo.adicionar(usuario)
        print(f"Usuário cadastrado com ID {usuario.id}.\n")

    def listar_usuarios(self):
        print("\n--- Lista de Usuários ---")
        usuarios = self.repo.listar_todos()
        if not usuarios:
            print("Nenhum usuário cadastrado.\n")
            return
        for u in usuarios:
            ano = f"{u.ano}" if u.ano is not None else "s/d"
            print(f"[{u.id}] {u.titulo} — {u.autor} ({ano}) | Disponível: {u.quantidade}")
        print("")

    def buscar_usuario(self):
        termo = input("\nDigite título ou autor para buscar: ").strip()
        if not termo:
            print("Termo vazio.\n")
            return
        encontrados = self.repo.buscar(termo)
        if not encontrados:
            print("Nenhum resultado encontrado.\n")
            return
        print(f"\nResultados para '{termo}':")
        for u in encontrados:
            ano = f"{u.ano}" if u.ano is not None else "s/d"
            print(f"[{u.id}] {u.titulo} — {u.autor} ({ano}) | Disponível: {u.quantidade}")
        print("")

    def remover_usuario(self):
        try:
            usuario_id = int(input("\nID do usuário a remover: "))
        except ValueError:
            print("ID inválido.\n")
            return
        ok = self.repo.remover(usuario_id)
        if ok:
            print("Usuário removido com sucesso.\n")
        else:
            print("Usuário não encontrado.\n")

    def emprestar(self):
        try:
            usuario_id = int(input("\nID do usuário para emprestar: "))
        except ValueError:
            print("ID inválido.\n")
            return
        usuario = self.repo.obter_por_id(usuario_id)
        if not usuario:
            print("Usuário não encontrado.\n")
            return
        if usuario.quantidade <= 0:
            print("Nenhuma cópia disponível.\n")
            return
        usuario.quantidade -= 1
        self.repo.atualizar(usuario)
        print(f"Usuário '{usuario.titulo}' emprestado. Restam {usuario.quantidade}.\n")

    def devolver(self):
        try:
            usuario_id = int(input("\nID do usuário para devolver: "))
        except ValueError:
            print("ID inválido.\n")
            return
        usuario = self.repo.obter_por_id(usuario_id)
        if not usuario:
            print("Usuário não encontrado.\n")
            return
        usuario.quantidade += 1
        self.repo.atualizar(usuario)
        print(f"Usuário '{usuario.titulo}' devolvido. Disponível: {usuario.quantidade}.\n")

    def editar_usuario(self):
        try:
            usuario_id = int(input("\nID do usuário para editar: "))
        except ValueError:
            print("ID inválido.\n")
            return
        usuario = self.repo.obter_por_id(usuario_id)
        if not usuario:
            print("Usuário não encontrado.\n")
            return

        print("Deixe em branco para manter o valor atual.")
        titulo = input(f"Título [{usuario.titulo}]: ").strip() or usuario.titulo
        autor = input(f"Autor [{usuario.autor}]: ").strip() or usuario.autor
        ano_raw = input(f"Ano [{usuario.ano if usuario.ano else 's/d'}]: ").strip()
        ano = int(ano_raw) if ano_raw.isdigit() else usuario.ano
        qtd_raw = input(f"Quantidade [{usuario.quantidade}]: ").strip()
        quantidade = int(qtd_raw) if qtd_raw.isdigit() else usuario.quantidade

        usuario.titulo = titulo
        usuario.autor = autor
        usuario.ano = ano
        usuario.quantidade = quantidade
        self.repo.atualizar(usuario)
        print("Usuário atualizado.\n")

    def menu(self):
        while True:
            print("=== Sistema de Biblioteca ===")
            print("1 - Cadastrar usuário")
            print("2 - Listar usuários")
            print("3 - Buscar usuário")
            print("4 - Editar usuário")
            print("5 - Remover usuário")
            print("6 - Emprestar usuário")
            print("7 - Devolver usuário")
            print("0 - Sair")
            opc = input("Escolha uma opção: ").strip()
            if opc == "1":
                self.cadastrar_usuario()
            elif opc == "2":
                self.listar_usuarios()
            elif opc == "3":
                self.buscar_usuario()
            elif opc == "4":
                self.editar_usuario()
            elif opc == "5":
                self.remover_usuario()
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