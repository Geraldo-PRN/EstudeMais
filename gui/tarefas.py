import tkinter as tk
from tkinter import ttk, messagebox
from database import get_conn

class TarefasFrame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.build()

    def build(self):
        tk.Label(self, text="Nova Tarefa", font=("Arial", 13)).place(x=10, y=10)
        tk.Label(self, text="Matéria:").place(x=10, y=50)
        self.combo_mat = ttk.Combobox(self, state="readonly")
        self.combo_mat.place(x=70, y=50, width=200)
        self.refresh_combo_mat()
        tk.Label(self, text="Título:").place(x=300, y=50)
        self.entry_titulo = tk.Entry(self)
        self.entry_titulo.place(x=350, y=50, width=150)
        tk.Label(self, text="Prazo (AAAA-MM-DD):").place(x=520, y=50)
        self.entry_prazo = tk.Entry(self)
        self.entry_prazo.place(x=650, y=50, width=100)
        tk.Label(self, text="Tipo:").place(x=10, y=85)
        self.combo_tipo = ttk.Combobox(self, values=["exercicio", "trabalho", "leitura"], state="readonly")
        self.combo_tipo.place(x=60, y=85, width=150)
        tk.Button(self, text="Adicionar", command=self.add_tarefa).place(x=230, y=83)
        self.tree = ttk.Treeview(self, columns=("Materia", "Título", "Prazo", "Tipo", "Concluída"), show="headings")
        self.tree.place(x=10, y=120, width=800, height=200)
        for col in ["Materia", "Título", "Prazo", "Tipo", "Concluída"]:
            self.tree.heading(col, text=col)
        tk.Button(self, text="Concluir Tarefa", command=self.concluir_tarefa).place(x=10, y=340)
        self.refresh_tarefas()

    def refresh_combo_mat(self):
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT id, nome FROM materia")
        self.combo_mat['values'] = [f"{id}: {nome}" for id, nome in c.fetchall()]
        conn.close()

    def add_tarefa(self):
        sel = self.combo_mat.get()
        titulo = self.entry_titulo.get().strip()
        prazo = self.entry_prazo.get().strip()
        tipo = self.combo_tipo.get()
        if not (sel and titulo and prazo and tipo):
            messagebox.showwarning("Tarefa", "Preencha todos os campos.")
            return
        materia_id = int(sel.split(":")[0])
        conn = get_conn()
        c = conn.cursor()
        c.execute('''INSERT INTO tarefa (materia_id, titulo, prazo, tipo)
                     VALUES (?,?,?,?)''', (materia_id, titulo, prazo, tipo))
        conn.commit()
        conn.close()
        self.entry_titulo.delete(0, tk.END)
        self.entry_prazo.delete(0, tk.END)
        self.combo_mat.set("")
        self.combo_tipo.set("")
        self.refresh_tarefas()

    def refresh_tarefas(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        conn = get_conn()
        c = conn.cursor()
        c.execute('''SELECT t.id, m.nome, t.titulo, t.prazo, t.tipo, t.concluida
                     FROM tarefa t
                     JOIN materia m ON m.id = t.materia_id
                     ORDER BY t.prazo ASC''')
        for id, nome, titulo, prazo, tipo, conc in c.fetchall():
            status = "Sim" if conc else "Não"
            self.tree.insert('', 'end', iid=id, values=(nome, titulo, prazo, tipo, status))
        conn.close()

    def concluir_tarefa(self):
        sel = self.tree.selection()
        if sel:
            tarefa_id = int(sel[0])
            conn = get_conn()
            c = conn.cursor()
            c.execute("UPDATE tarefa SET concluida=1 WHERE id=?", (tarefa_id,))
            conn.commit()
            conn.close()
            self.refresh_tarefas()