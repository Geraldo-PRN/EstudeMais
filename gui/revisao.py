import tkinter as tk
from tkinter import ttk, messagebox
from database import get_conn

class RevisaoFrame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.build()

    def build(self):
        tk.Label(self, text="Revisões Agendadas", font=("Arial", 13)).place(x=10, y=10)

        # Tabela de revisões
        self.tree = ttk.Treeview(self, columns=("ID", "Matéria", "Data Revisão", "Realizada"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Matéria", text="Matéria")
        self.tree.heading("Data Revisão", text="Data Revisão")
        self.tree.heading("Realizada", text="Realizada")
        self.tree.column("ID", width=40, anchor="center")
        self.tree.column("Matéria", width=210)
        self.tree.column("Data Revisão", width=100)
        self.tree.column("Realizada", width=80, anchor="center")
        self.tree.place(x=10, y=50, width=430, height=320)

        tk.Button(self, text="Marcar como realizada", command=self.marcar_realizada).place(x=460, y=50, width=170)
        tk.Button(self, text="Remover revisão", command=self.remover_revisao).place(x=460, y=95, width=170)

        self.refresh()

    def refresh(self):
        self.refresh_lista_revisoes()

    def refresh_lista_revisoes(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        conn = get_conn()
        c = conn.cursor()
        c.execute('''SELECT revisao.id, materia.nome, revisao.data_revisao, revisao.realizada
                     FROM revisao
                     JOIN materia ON materia.id = revisao.materia_id
                     ORDER BY revisao.data_revisao ASC''')
        for id_, materia, data_rev, realizada in c.fetchall():
            status = "Sim" if realizada else "Não"
            self.tree.insert('', 'end', values=(id_, materia, data_rev, status))
        conn.close()

    def marcar_realizada(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Revisão", "Selecione uma revisão para marcar como realizada.")
            return
        item = self.tree.item(selected[0])
        id_revisao = item['values'][0]
        conn = get_conn()
        c = conn.cursor()
        c.execute("UPDATE revisao SET realizada=1 WHERE id=?", (id_revisao,))
        conn.commit()
        conn.close()
        self.refresh()

    def remover_revisao(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Revisão", "Selecione uma revisão para remover.")
            return
        item = self.tree.item(selected[0])
        id_revisao = item['values'][0]
        if messagebox.askyesno("Remover", "Tem certeza que deseja remover esta revisão?"):
            conn = get_conn()
            c = conn.cursor()
            c.execute("DELETE FROM revisao WHERE id=?", (id_revisao,))
            conn.commit()
            conn.close()
            self.refresh()