from models.tarefa_model import TarefaModel

class TarefaController:
    def __init__(self):
        self.model = TarefaModel()

    def cadastrar_tarefa(self, titulo, assunto, data, status):
        self.model.cadastrar(titulo, assunto, data, status)

    def listar_tarefas(self, busca=""):
        return self.model.listar(busca)

    def atualizar_tarefa(self, tarefa_id, titulo, assunto, data, status):
        self.model.atualizar(tarefa_id, titulo, assunto, data, status)

    def deletar_tarefa(self, tarefa_id):
        self.model.deletar(tarefa_id)

     # Novo método para unificar cadastro e atualização
    def salvar_tarefa(self, tarefa):
        if tarefa["id"]:  # Se já existe → atualizar
            self.atualizar_tarefa(
                tarefa["id"],
                tarefa["titulo"],
                tarefa["assunto"],
                tarefa["data"],
                tarefa["status"]
            )
        else:  # Se não tem id → cadastrar
            self.cadastrar_tarefa(
                tarefa["titulo"],
                tarefa["assunto"],
                tarefa["data"],
                tarefa["status"]
            )
