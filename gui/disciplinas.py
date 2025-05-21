import tkinter as tk
from tkinter import ttk, messagebox
from database import get_conn

class DisciplinasFrame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.build()

    def build(self):
        # Título
        tk.Label(self, text="Gerenciar Disciplinas", font=("Arial", 13)).place(x=10, y=10)

        # Lista de Disciplinas
        tk.Label(self, text="Disciplinas cadastradas:").place(x=10, y=50)
        self.tree = ttk.Treeview(self, columns=("ID", "Disciplina"), show="headings", selectmode="browse")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Disciplina", text="Nome da Disciplina")
        self.tree.column("ID", width=40, anchor="center")
        self.tree.column("Disciplina", width=250)
        self.tree.place(x=10, y=75, width=300, height=250)
        self.refresh_disciplinas()

        # Nova disciplina
        tk.Label(self, text="Nova disciplina:").place(x=330, y=75)
        self.entry_nova_disciplina = tk.Entry(self)
        self.entry_nova_disciplina.place(x=440, y=75, width=170)
        tk.Button(self, text="Inserir", command=self.adicionar_disciplina).place(x=620, y=73, width=70)

        # Botão de Remover
        tk.Button(self, text="Remover selecionada", command=self.remover_disciplina).place(x=330, y=120, width=150)

        # Nova matéria para a disciplina selecionada
        tk.Label(self, text="Nova matéria:").place(x=330, y=180)
        self.entry_nova_materia = tk.Entry(self)
        self.entry_nova_materia.place(x=420, y=180, width=190)
        tk.Button(self, text="Inserir Matéria", command=self.adicionar_materia).place(x=620, y=178, width=90)

        # Lista de matérias da disciplina selecionada
        tk.Label(self, text="Matérias da disciplina selecionada:").place(x=330, y=230)
        self.tree_materias = ttk.Treeview(self, columns=("ID", "Matéria"), show="headings", selectmode="browse")
        self.tree_materias.heading("ID", text="ID")
        self.tree_materias.heading("Matéria", text="Nome da Matéria")
        self.tree_materias.column("ID", width=40, anchor="center")
        self.tree_materias.column("Matéria", width=220)
        self.tree_materias.place(x=330, y=255, width=300, height=120)
        self.tree.bind("<<TreeviewSelect>>", self.on_disciplina_select)
        self.refresh_materias(None)

        tk.Button(self, text="Remover Matéria", command=self.remover_materia).place(x=640, y=255, width=110)

    def refresh_disciplinas(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT id, nome FROM disciplina ORDER BY nome ASC")
        for id_, nome in c.fetchall():
            self.tree.insert('', 'end', values=(id_, nome))
        conn.close()

    def adicionar_disciplina(self):
        nome = self.entry_nova_disciplina.get().strip()
        if not nome:
            messagebox.showwarning("Disciplinas", "Informe o nome da disciplina.")
            return
        conn = get_conn()
        c = conn.cursor()
        c.execute("INSERT INTO disciplina (nome) VALUES (?)", (nome,))
        conn.commit()
        conn.close()
        self.entry_nova_disciplina.delete(0, tk.END)
        self.refresh_disciplinas()

    def remover_disciplina(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Disciplinas", "Selecione uma disciplina para remover.")
            return
        item = self.tree.item(selected[0])
        id_disc, nome = item['values']
        if messagebox.askyesno("Remover", f"Remover disciplina '{nome}'? Todas as matérias e sessões associadas também serão removidas!"):
            conn = get_conn()
            c = conn.cursor()
            # Remove matérias dessa disciplina
            c.execute("DELETE FROM materia WHERE disciplina_id=?", (id_disc,))
            # Remove sessões dessa disciplina (opcional, se você quiser manter a integridade)
            c.execute("DELETE FROM sessao WHERE disciplina_id=?", (id_disc,))
            # Remove disciplina
            c.execute("DELETE FROM disciplina WHERE id=?", (id_disc,))
            conn.commit()
            conn.close()
            self.refresh_disciplinas()
            self.refresh_materias(None)

    def on_disciplina_select(self, event):
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            id_disc = item['values'][0]
            self.refresh_materias(id_disc)
        else:
            self.refresh_materias(None)

    def refresh_materias(self, disciplina_id):
        for row in self.tree_materias.get_children():
            self.tree_materias.delete(row)
        if not disciplina_id:
            return
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT id, nome FROM materia WHERE disciplina_id=? ORDER BY nome ASC", (disciplina_id,))
        for id_, nome in c.fetchall():
            self.tree_materias.insert('', 'end', values=(id_, nome))
        conn.close()

    def adicionar_materia(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Matéria", "Selecione uma disciplina primeiro.")
            return
        nome_mat = self.entry_nova_materia.get().strip()
        if not nome_mat:
            messagebox.showwarning("Matéria", "Informe o nome da matéria.")
            return
        item = self.tree.item(selection[0])
        id_disc = item['values'][0]
        conn = get_conn()
        c = conn.cursor()
        c.execute("INSERT INTO materia (nome, disciplina_id) VALUES (?, ?)", (nome_mat, id_disc))
        conn.commit()
        conn.close()
        self.entry_nova_materia.delete(0, tk.END)
        self.refresh_materias(id_disc)

    def remover_materia(self):
        selection_mat = self.tree_materias.selection()
        if not selection_mat:
            messagebox.showwarning("Matéria", "Selecione uma matéria para remover.")
            return
        item = self.tree_materias.item(selection_mat[0])
        id_mat, nome = item['values']
        if messagebox.askyesno("Remover Matéria", f"Remover matéria '{nome}'? Todas as sessões associadas também serão removidas!"):
            conn = get_conn()
            c = conn.cursor()
            # Remove sessões dessa matéria (opcional, para manter integridade)
            c.execute("DELETE FROM sessao WHERE materia_id=?", (id_mat,))
            # Remove matéria
            c.execute("DELETE FROM materia WHERE id=?", (id_mat,))
            conn.commit()
            conn.close()
            # Atualiza lista de matérias
            selection = self.tree.selection()
            if selection:
                id_disc = self.tree.item(selection[0])['values'][0]
                self.refresh_materias(id_disc)
            else:
                self.refresh_materias(None)