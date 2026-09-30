from datetime import datetime, timedelta
from models.agenda_model import ContatoModel, CompromissoModel, LembreteModel
import database as banco

class ControladorAgenda:
    def __init__(self):
        banco.inicializar_banco()

    def obter_contatos(self):
        return ContatoModel.listar_todos()

    def adicionar_contato(self, nome, telefone=None, email=None):
        try:
            if not nome or not nome.strip():
                return {"sucesso": False, "erro": "Nome é obrigatório."}
            novo_id = ContatoModel.criar(nome.strip(), telefone, email)
            return {"sucesso": True, "id": novo_id}
        except Exception as erro:
            return {"sucesso": False, "erro": str(erro)}

    def atualizar_contato(self, contato_id, nome, telefone=None, email=None):
        try:
            if not nome or not nome.strip():
                return {"sucesso": False, "erro": "Nome é obrigatório."}
            sucesso = ContatoModel.atualizar(int(contato_id), nome.strip(), telefone, email)
            return {"sucesso": sucesso}
        except Exception as erro:
            return {"sucesso": False, "erro": str(erro)}

    def excluir_contato(self, contato_id):
        try:
            sucesso = ContatoModel.excluir(int(contato_id))
            return {"sucesso": sucesso}
        except Exception as erro:
            return {"sucesso": False, "erro": str(erro)}

    def pesquisar_contatos(self, termo):
        return ContatoModel.pesquisar(termo)

    def obter_contatos_frequentes(self):
        return ContatoModel.obter_frequentes()

    def carregar_dados_exemplo(self):
        conexao = banco.obter_conexao()
        try:
            cursor = conexao.cursor()
            cursor.execute("SELECT 1 FROM dados_exemplo WHERE id = 1")
            if cursor.fetchone():
                return {"sucesso": True, "ja_carregados": True}

            contatos = [
                ("Ana Souza", "(11) 91234-5678", "ana.souza@example.com"),
                ("Bruno Lima", "(11) 92345-6789", "bruno.lima@example.com"),
                ("Carla Mendes", "(11) 93456-7890", "carla.mendes@example.com"),
            ]
            contato_ids = []
            for nome, telefone, email in contatos:
                cursor.execute(
                    "INSERT INTO contatos (nome, telefone, email) VALUES (?, ?, ?)",
                    (nome, telefone, email)
                )
                contato_ids.append(cursor.lastrowid)

            inicio = datetime.now() + timedelta(hours=1)
            compromissos = [
                ("Reunião de alinhamento", "Confirmar os próximos passos.", 0, 0),
                ("Revisão de orçamento", "Levar a proposta atualizada.", 1, 1),
                ("Atendimento de demonstração", "Apresentar as opções disponíveis.", 2, 4),
                ("Retorno sobre proposta", "Entrar em contato após a avaliação.", 0, 15),
            ]
            for titulo, observacao, contato_indice, dias_depois in compromissos:
                data_hora = inicio + timedelta(days=dias_depois)
                cursor.execute(
                    """INSERT INTO compromissos
                       (titulo, observacao, data, hora, contato_id, concluido)
                       VALUES (?, ?, ?, ?, ?, 0)""",
                    (
                        titulo,
                        observacao,
                        data_hora.strftime("%Y-%m-%d"),
                        data_hora.strftime("%H:%M"),
                        contato_ids[contato_indice],
                    )
                )

            cursor.executemany(
                "INSERT INTO lembretes (titulo, observacao, concluido) VALUES (?, ?, 0)",
                [
                    ("Separar documentos do cliente", "Deixar os arquivos prontos para o próximo atendimento."),
                    ("Revisar agenda da semana", "Conferir horários e preparar os materiais."),
                ]
            )
            cursor.execute(
                "INSERT INTO dados_exemplo (id, carregado_em) VALUES (1, ?)",
                (datetime.now().isoformat(timespec="seconds"),)
            )
            conexao.commit()
            return {"sucesso": True, "ja_carregados": False}
        except Exception as erro:
            conexao.rollback()
            return {"sucesso": False, "erro": str(erro)}
        finally:
            conexao.close()

    def _data_hora_compromisso_ja_passou(self, data, hora):
        data_hora = datetime.strptime(f"{data} {hora}", "%Y-%m-%d %H:%M")
        return data_hora < datetime.now()

    def adicionar_compromisso(self, titulo, observacao, data, hora, contato_id=None):
        try:
            if not titulo or not titulo.strip():
                return {"sucesso": False, "erro": "Título é obrigatório."}
            if not data or not data.strip():
                return {"sucesso": False, "erro": "Data é obrigatória."}
            if not hora or not hora.strip():
                return {"sucesso": False, "erro": "Hora é obrigatória."}
            if self._data_hora_compromisso_ja_passou(data, hora):
                return {"sucesso": False, "erro": "O horário ou data informada já passou."}
            
            c_id = int(contato_id) if contato_id and str(contato_id).isdigit() else None
            novo_id = CompromissoModel.criar(titulo.strip(), observacao, data, hora, c_id)
            return {"sucesso": True, "id": novo_id}
        except Exception as erro:
            return {"sucesso": False, "erro": str(erro)}

    def obter_compromisso(self, compromisso_id):
        return CompromissoModel.obter_por_id(int(compromisso_id))

    def atualizar_compromisso(self, id, titulo, observacao, data, hora, contato_id=None, concluido=0):
        try:
            if not titulo or not titulo.strip():
                return {"sucesso": False, "erro": "Título é obrigatório."}
            if not data or not data.strip():
                return {"sucesso": False, "erro": "Data é obrigatória."}
            if not hora or not hora.strip():
                return {"sucesso": False, "erro": "Hora é obrigatória."}
            if self._data_hora_compromisso_ja_passou(data, hora):
                return {"sucesso": False, "erro": "O horário ou data informada já passou."}
            
            c_id = int(contato_id) if contato_id and str(contato_id).isdigit() else None
            sucesso = CompromissoModel.atualizar(int(id), titulo.strip(), observacao, data, hora, c_id, int(concluido))
            return {"sucesso": sucesso}
        except Exception as erro:
            return {"sucesso": False, "erro": str(erro)}

    def excluir_compromisso(self, id):
        try:
            sucesso = CompromissoModel.excluir(int(id))
            return {"sucesso": sucesso}
        except Exception as erro:
            return {"sucesso": False, "erro": str(erro)}

    def concluir_compromisso(self, id, status=1):
        try:
            sucesso = CompromissoModel.alterar_status_concluido(int(id), int(status))
            return {"sucesso": sucesso}
        except Exception as erro:
            return {"sucesso": False, "erro": str(erro)}

    def adicionar_lembrete(self, titulo, observacao):
        try:
            if not titulo or not titulo.strip():
                return {"sucesso": False, "erro": "Título é obrigatório."}
            novo_id = LembreteModel.criar(titulo.strip(), observacao)
            return {"sucesso": True, "id": novo_id}
        except Exception as erro:
            return {"sucesso": False, "erro": str(erro)}

    def atualizar_lembrete(self, id, titulo, observacao, concluido=0):
        try:
            if not titulo or not titulo.strip():
                return {"sucesso": False, "erro": "Título é obrigatório."}
            sucesso = LembreteModel.atualizar(int(id), titulo.strip(), observacao, int(concluido))
            return {"sucesso": sucesso}
        except Exception as erro:
            return {"sucesso": False, "erro": str(erro)}

    def excluir_lembrete(self, id):
        try:
            sucesso = LembreteModel.excluir(int(id))
            return {"sucesso": sucesso}
        except Exception as erro:
            return {"sucesso": False, "erro": str(erro)}

    def concluir_lembrete(self, id, status=1):
        try:
            sucesso = LembreteModel.alterar_status_concluido(int(id), int(status))
            return {"sucesso": sucesso}
        except Exception as erro:
            return {"sucesso": False, "erro": str(erro)}

    def obter_agenda(self, data_str):
        agora = datetime.now()
        hoje_str = agora.strftime("%Y-%m-%d")
        hora_atual = agora.strftime("%H:%M")

        lembretes = LembreteModel.listar(apenas_ativos=False)
        compromissos = CompromissoModel.listar_por_data(data_str)

        if data_str == hoje_str:
            compromissos = [
                c for c in compromissos
                if not (c["concluido"] == 0 and c["hora"] < hora_atual)
            ]

        return {
            "lembretes": lembretes,
            "compromissos": compromissos,
            "hoje": hoje_str
        }

    def obter_agenda_periodo(self, data_inicio, data_fim):
        compromissos = CompromissoModel.listar_por_periodo(data_inicio, data_fim)
        return {"compromissos": compromissos}

    def pesquisar_compromissos(self, tipo, termo):
        if tipo == "contato":
            compromissos = CompromissoModel.pesquisar_por_contato(termo)
        else:
            compromissos = CompromissoModel.pesquisar_por_titulo(termo)
        return {"compromissos": compromissos}
