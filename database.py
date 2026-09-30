import os
import sys
import sqlite3

if hasattr(sys, '_MEIPASS'):
    pasta_banco = os.path.join(os.environ.get('APPDATA', os.path.expanduser('~')), 'clique.agenda')
    if not os.path.exists(pasta_banco):
        os.makedirs(pasta_banco)
    ARQUIVO_BANCO = os.path.join(pasta_banco, "agenda.db")
else:
    ARQUIVO_BANCO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "agenda.db")

def obter_conexao():
    conexao = sqlite3.connect(ARQUIVO_BANCO)
    conexao.row_factory = sqlite3.Row
    conexao.execute("PRAGMA foreign_keys = ON;")
    return conexao

def inicializar_banco():
    conexao = obter_conexao()
    cursor = conexao.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS contatos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        telefone TEXT,
        email TEXT
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS compromissos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titulo TEXT NOT NULL,
        observacao TEXT,
        data TEXT NOT NULL,
        hora TEXT NOT NULL,
        contato_id INTEGER,
        concluido INTEGER DEFAULT 0,
        FOREIGN KEY (contato_id) REFERENCES contatos(id) ON DELETE SET NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS lembretes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titulo TEXT NOT NULL,
        observacao TEXT,
        concluido INTEGER DEFAULT 0
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dados_exemplo (
        id INTEGER PRIMARY KEY CHECK (id = 1),
        carregado_em TEXT NOT NULL
    );
    """)

    conexao.commit()
    conexao.close()