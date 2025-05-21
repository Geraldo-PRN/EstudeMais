import tkinter as tk
from tkinter import ttk, messagebox
from database import get_conn
from datetime import date, timedelta

class PlanejamentoFrame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.build()

    def build(self):
        tk.Label(self, text="Planejamento de Estudos", font=("Arial", 13)).place(x=10, y=10)
        tk.Label(self, text="Matéria:").place(x=10, y=50)
        self.combo_mat = ttk.Combobox(self, state="readonly")
        self.combo_mat.place(x=70, y=50, width=200)
        self.refresh_combo_mat()
        tk.Label(self, text="Tipo:").place(x=300, y=50)
        self.combo_tipo = ttk.Combobox(self, values=["diario", "semanal", "mensal"], state="readonly")
        self.combo_tipo.place(x=340, y=50, width=80)
        tk.Label(self, text="Meta (min):").place(x=440, y=50)
        self.entry_meta = tk.Entry(self)
        self.entry_meta.place(x=520, y=50, width=60)
        tk.Button(self, text="Adicionar Meta", command=self.add_planejamento).place(x=600, y=48)
        self.tree = ttk.Treeview(self, columns=("Materia", "Tipo", "Meta", "Inicio", "Fim"), show="headings")
        self.tree.place(x=10, y=90, width=800, height=200)
        for col in ["Materia", "Tipo", "Meta", "Inicio", "Fim"]:
            self.tree.heading(col, text=col)
        self.refresh_planejamento()

    def refresh_combo_mat(self):
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT id, nome FROM materia")
        self.combo_mat['values'] = [f"{id}: {nome}" for id, nome in c.fetchall()]
        conn.close()

    def add_planejamento(self):
        sel = self.combo_mat.get()
        tipo = self.combo_tipo.get()
        meta = self.entry_meta.get()
        if not (sel and tipo and meta.isdigit()):
            messagebox.showwarning("Planejamento", "Preencha todos os campos corretamente.")
            return
        materia_id = int(sel.split(":")[0])
        meta = int(meta)
        hoje = date.today()
        if tipo == "diario":
            inicio, fim = hoje, hoje
        elif tipo == "semanal":
            inicio = hoje - timedelta(days=hoje.weekday())
            fim = inicio + timedelta(days=6)
        else: # mensal
            inicio = hoje.replace(day=1)
            fim = (inicio.replace(month=inicio.month % 12 + 1, day=1) - timedelta(days=1)) if inicio.month < 12 else date(hoje.year, 12, 31)
        conn = get_conn()
        c = conn.cursor()
        c.execute('''INSERT INTO planejamento
                     (materia_id, tipo, meta_minutos, periodo_inicio, periodo_fim)
                     VALUES (?,?,?,?,?)''',
                  (materia_id, tipo, meta, inicio.isoformat(), fim.isoformat()))
        conn.commit()
        conn.close()
        self.refresh_planejamento()

    def refresh_planejamento(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        conn = get_conn()
        c = conn.cursor()
        c.execute('''SELECT m.nome, p.tipo, p.meta_minutos, p.periodo_inicio, p.periodo_fim
                     FROM planejamento p
                     JOIN materia m ON m.id = p.materia_id
                     ORDER BY p.periodo_inicio DESC''')
        for nome, tipo, meta, ini, fim in c.fetchall():
            self.tree.insert('', 'end', values=(nome, tipo, meta, ini, fim))
        conn.close()