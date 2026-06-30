from datetime import datetime
from models.agenda_model import ContatoModel, CompromissoModel, LembreteModel
import database as banco

class ControladorAgenda:
    def __init__(self, logger):
        self.logger = logger
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
