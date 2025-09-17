from utils.db_connection import get_connection
from datetime import datetime

class TarefaModel:
    def __init__(self):
        self.conn = get_connection()
        self.cursor = self.conn.cursor(dictionary=True)

    def _converter_data(self, data):
        """Converte data do formato DD/MM/YYYY para YYYY-MM-DD"""
        try:
            return datetime.strptime(data, "%d/%m/%Y").strftime("%Y-%m-%d")
        except ValueError:
            # Retorna None ou lança erro se o formato estiver incorreto
            return None

    def cadastrar(self, titulo, assunto, data, status):
        data_mysql = self._converter_data(data)
        sql = "INSERT INTO tarefas (titulo, assunto, data, status) VALUES (%s, %s, %s, %s)"
        self.cursor.execute(sql, (titulo, assunto, data_mysql, status))
        self.conn.commit()

    def listar(self, busca=""):
        sql = "SELECT * FROM tarefas WHERE titulo LIKE %s OR status LIKE %s ORDER BY data DESC"
        self.cursor.execute(sql, (f"%{busca}%", f"%{busca}%"))
        return self.cursor.fetchall()

    def atualizar(self, tarefa_id, titulo, assunto, data, status):
        data_mysql = self._converter_data(data)
        sql = "UPDATE tarefas SET titulo=%s, assunto=%s, data=%s, status=%s WHERE id=%s"
        self.cursor.execute(sql, (titulo, assunto, data_mysql, status, tarefa_id))
        self.conn.commit()

    def deletar(self, tarefa_id):
        sql = "DELETE FROM tarefas WHERE id=%s"
        self.cursor.execute(sql, (tarefa_id,))
        self.conn.commit()
