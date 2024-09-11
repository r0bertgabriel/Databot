#%%
import sqlite3
class AgendaDB:
    def __init__(self, arquivo):
        self.conn = sqlite3.connect(arquivo)
        self.cursor = self.conn.cursor()

    def inserir(self, nome, telefone):
        consulta = 'INSERT OR IGNORE INTO agenda(nome, telefone) VALUES(?,?)'
        self.cursor.execute(consulta, (nome, telefone))
        self.conn.commit()
        
    def editar(self, nome, telefone, id):
        consulta = 'UPDATE  OR IGNORE agenda SET nome=?, telefone=? WHERE id=?'
        self.cursor.execute(consulta, (nome, telefone, id))
        self.conn.commit()

    def excluir(self, id):
        consulta = 'DELETE FROM agenda WHERE id=?'
        self.cursor.execute(consulta, (id,)) #',' no final = tupla
        self.conn.commit()
        
    def listar(self):
        self.cursor.execute('SELECT * FROM agenda')
        for linha in self.cursor.fetchall():
            print(linha)

    def fechar(self):
        self.conn.close()
        self.cursor.close()

# telefone tem valor único

if __name__ == '__main__':
    agenda = AgendaDB('agenda.db')
    agenda.inserir('Robert', '222222')
    agenda.inserir('Fernanda', '333333')
    agenda.inserir('Lucas', '444444')
    agenda.inserir('Manoela', '555555')

# %%
agenda.listar()
# %%
agenda.editar('Robert', '000000', 3)
# %%
