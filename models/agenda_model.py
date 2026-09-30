import database as banco

class ContatoModel:
    @staticmethod
    def criar(nome, telefone=None, email=None):
        conexao = banco.obter_conexao()
        cursor = conexao.cursor()
        cursor.execute(
            "INSERT INTO contatos (nome, telefone, email) VALUES (?, ?, ?)",
            (nome, telefone, email)
        )
        novo_id = cursor.lastrowid
        conexao.commit()
        conexao.close()
        return novo_id

    @staticmethod
    def listar_todos():
        conexao = banco.obter_conexao()
        cursor = conexao.cursor()
        cursor.execute("SELECT * FROM contatos ORDER BY nome COLLATE NOCASE ASC")
        linhas = cursor.fetchall()
        conexao.close()
        return [dict(l) for l in linhas]

    @staticmethod
    def atualizar(contato_id, nome, telefone=None, email=None):
        conexao = banco.obter_conexao()
        cursor = conexao.cursor()
        cursor.execute(
            "UPDATE contatos SET nome = ?, telefone = ?, email = ? WHERE id = ?",
            (nome, telefone, email, contato_id)
        )
        conexao.commit()
        conexao.close()
        return cursor.rowcount > 0

    @staticmethod
    def excluir(contato_id):
        conexao = banco.obter_conexao()
        cursor = conexao.cursor()
        cursor.execute("DELETE FROM contatos WHERE id = ?", (contato_id,))
        conexao.commit()
        conexao.close()
        return cursor.rowcount > 0

    @staticmethod
    def pesquisar(termo):
        conexao = banco.obter_conexao()
        cursor = conexao.cursor()
        t = f"%{termo}%"
        cursor.execute(
            "SELECT * FROM contatos WHERE nome LIKE ? OR telefone LIKE ? OR email LIKE ? ORDER BY nome COLLATE NOCASE ASC",
            (t, t, t)
        )
        linhas = cursor.fetchall()
        conexao.close()
        return [dict(l) for l in linhas]

    @staticmethod
    def obter_frequentes():
        conexao = banco.obter_conexao()
        cursor = conexao.cursor()
        cursor.execute("""
            SELECT co.id, co.nome, COUNT(c.id) as frequencia
            FROM contatos co
            INNER JOIN compromissos c ON c.contato_id = co.id
            GROUP BY co.id
            ORDER BY frequencia DESC, co.nome COLLATE NOCASE ASC
            LIMIT 3
        """)
        linhas = cursor.fetchall()
        conexao.close()
        return [dict(l) for l in linhas]


class CompromissoModel:
    @staticmethod
    def criar(titulo, observacao, data, hora, contato_id=None):
        conexao = banco.obter_conexao()
        cursor = conexao.cursor()
        cursor.execute(
            "INSERT INTO compromissos (titulo, observacao, data, hora, contato_id, concluido) VALUES (?, ?, ?, ?, ?, 0)",
            (titulo, observacao, data, hora, contato_id)
        )
        novo_id = cursor.lastrowid
        conexao.commit()
        conexao.close()
        return novo_id

    @staticmethod
    def obter_por_id(compromisso_id):
        conexao = banco.obter_conexao()
        cursor = conexao.cursor()
        cursor.execute("""
            SELECT c.*, co.nome as contato_nome, co.telefone as contato_telefone, co.email as contato_email
            FROM compromissos c
            LEFT JOIN contatos co ON c.contato_id = co.id
            WHERE c.id = ?
        """, (compromisso_id,))
        linha = cursor.fetchone()
        conexao.close()
        return dict(linha) if linha else None

    @staticmethod
    def listar_por_data(data_str):
        conexao = banco.obter_conexao()
        cursor = conexao.cursor()
        cursor.execute("""
            SELECT c.*, co.nome as contato_nome
            FROM compromissos c
            LEFT JOIN contatos co ON c.contato_id = co.id
            WHERE c.data = ?
            ORDER BY c.concluido ASC, c.hora ASC
        """, (data_str,))
        linhas = cursor.fetchall()
        conexao.close()
        return [dict(l) for l in linhas]

    @staticmethod
    def listar_por_periodo(data_inicio, data_fim):
        conexao = banco.obter_conexao()
        cursor = conexao.cursor()
        cursor.execute("""
            SELECT c.*, co.nome as contato_nome
            FROM compromissos c
            LEFT JOIN contatos co ON c.contato_id = co.id
            WHERE c.data >= ? AND c.data <= ?
            ORDER BY c.data ASC, c.hora ASC
        """, (data_inicio, data_fim))
        linhas = cursor.fetchall()
        conexao.close()
        return [dict(l) for l in linhas]

    @staticmethod
    def atualizar(compromisso_id, titulo, observacao, data, hora, contato_id=None, concluido=0):
        conexao = banco.obter_conexao()
        cursor = conexao.cursor()
        cursor.execute(
            "UPDATE compromissos SET titulo = ?, observacao = ?, data = ?, hora = ?, contato_id = ?, concluido = ? WHERE id = ?",
            (titulo, observacao, data, hora, contato_id, concluido, compromisso_id)
        )
        conexao.commit()
        conexao.close()
        return cursor.rowcount > 0

    @staticmethod
    def excluir(compromisso_id):
        conexao = banco.obter_conexao()
        cursor = conexao.cursor()
        cursor.execute("DELETE FROM compromissos WHERE id = ?", (compromisso_id,))
        conexao.commit()
        conexao.close()
        return cursor.rowcount > 0

    @staticmethod
    def alterar_status_concluido(compromisso_id, status=1):
        conexao = banco.obter_conexao()
        cursor = conexao.cursor()
        cursor.execute("UPDATE compromissos SET concluido = ? WHERE id = ?", (status, compromisso_id))
        conexao.commit()
        conexao.close()
        return cursor.rowcount > 0

    @staticmethod
    def pesquisar_por_titulo(termo):
        conexao = banco.obter_conexao()
        cursor = conexao.cursor()
        t = f"%{termo}%"
        cursor.execute("""
            SELECT c.*, co.nome as contato_nome
            FROM compromissos c
            LEFT JOIN contatos co ON c.contato_id = co.id
            WHERE c.titulo LIKE ? OR c.observacao LIKE ?
            ORDER BY c.data DESC, c.hora DESC
        """, (t, t))
        linhas = cursor.fetchall()
        conexao.close()
        return [dict(l) for l in linhas]

    @staticmethod
    def pesquisar_por_contato(termo):
        conexao = banco.obter_conexao()
        cursor = conexao.cursor()
        t = f"%{termo}%"
        cursor.execute("""
            SELECT c.*, co.nome as contato_nome
            FROM compromissos c
            INNER JOIN contatos co ON c.contato_id = co.id
            WHERE co.nome LIKE ?
            ORDER BY c.data DESC, c.hora DESC
        """, (t,))
        linhas = cursor.fetchall()
        conexao.close()
        return [dict(l) for l in linhas]


class LembreteModel:
    @staticmethod
    def criar(titulo, observacao):
        conexao = banco.obter_conexao()
        cursor = conexao.cursor()
        cursor.execute(
            "INSERT INTO lembretes (titulo, observacao, concluido) VALUES (?, ?, 0)",
            (titulo, observacao)
        )
        novo_id = cursor.lastrowid
        conexao.commit()
        conexao.close()
        return novo_id

    @staticmethod
    def listar(apenas_ativos=False):
        conexao = banco.obter_conexao()
        cursor = conexao.cursor()
        if apenas_ativos:
            cursor.execute("SELECT * FROM lembretes WHERE concluido = 0 ORDER BY id DESC")
        else:
            cursor.execute("SELECT * FROM lembretes ORDER BY concluido ASC, id DESC")
        linhas = cursor.fetchall()
        conexao.close()
        return [dict(l) for l in linhas]

    @staticmethod
    def atualizar(lembrete_id, titulo, observacao, concluido=0):
        conexao = banco.obter_conexao()
        cursor = conexao.cursor()
        cursor.execute(
            "UPDATE lembretes SET titulo = ?, observacao = ?, concluido = ? WHERE id = ?",
            (titulo, observacao, concluido, lembrete_id)
        )
        conexao.commit()
        conexao.close()
        return cursor.rowcount > 0

    @staticmethod
    def excluir(lembrete_id):
        conexao = banco.obter_conexao()
        cursor = conexao.cursor()
        cursor.execute("DELETE FROM lembretes WHERE id = ?", (lembrete_id,))
        conexao.commit()
        conexao.close()
        return cursor.rowcount > 0

    @staticmethod
    def alterar_status_concluido(lembrete_id, status=1):
        conexao = banco.obter_conexao()
        cursor = conexao.cursor()
        cursor.execute("UPDATE lembretes SET concluido = ? WHERE id = ?", (status, lembrete_id))
        conexao.commit()
        conexao.close()
        return cursor.rowcount > 0
    
    