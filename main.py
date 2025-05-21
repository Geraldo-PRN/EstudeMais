import tkinter as tk
from tkinter import ttk, messagebox
from database import setup_db
from gui.disciplinas import DisciplinasFrame
from gui.planejamento import PlanejamentoFrame
from gui.sessoes import SessoesFrame
from gui.tarefas import TarefasFrame
from gui.graficos import GraficosFrame
from gui.revisao import RevisaoFrame
from pomodoro import PomodoroTimer

class PomodoroFrame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.build()

    def build(self):
        tk.Label(self, text="Modo Pomodoro", font=("Arial", 13)).place(x=10, y=10)
        tk.Label(self, text="Tempo de estudo (min):").place(x=10, y=50)
        self.entry_estudo = tk.Entry(self)
        self.entry_estudo.place(x=150, y=50, width=60)
        tk.Label(self, text="Tempo de pausa (min):").place(x=230, y=50)
        self.entry_pausa = tk.Entry(self)
        self.entry_pausa.place(x=360, y=50, width=60)
        self.lbl_status = tk.Label(self, text="", font=("Arial", 15), fg="darkblue")
        self.lbl_status.place(x=10, y=100)
        self.pomodoro = PomodoroTimer(
            self.lbl_status,
            self.entry_estudo.get,
            self.entry_pausa.get
        )
        tk.Button(self, text="Iniciar Pomodoro", command=self.pomodoro.start).place(x=440, y=48)

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Controle de Estudos")
        self.geometry("900x700")
        self.resizable(False, False)
        self.tabs = ttk.Notebook(self)
        self.tabs.pack(fill="both", expand=True)

        # Instancia os frames
        self.frame_disc_mat = DisciplinasFrame(self.tabs)
        self.frame_planejar = PlanejamentoFrame(self.tabs)
        self.frame_sessoes = SessoesFrame(self.tabs)
        self.frame_tarefas = TarefasFrame(self.tabs)
        self.frame_graficos = GraficosFrame(self.tabs)
        self.frame_revisao = RevisaoFrame(self.tabs)
        self.frame_pomodoro = PomodoroFrame(self.tabs)

        # Referências cruzadas para atualização em tempo real entre guias
        self.frame_disc_mat.frame_sessoes = self.frame_sessoes
        self.frame_sessoes.frame_disc_mat = self.frame_disc_mat
        self.frame_planejar.frame_disc_mat = self.frame_disc_mat
        self.frame_tarefas.frame_disc_mat = self.frame_disc_mat
        self.frame_graficos.frame_disc_mat = self.frame_disc_mat
        self.frame_revisao.frame_disc_mat = self.frame_disc_mat
        self.frame_sessoes.frame_revisao = self.frame_revisao

        self.tabs.add(self.frame_disc_mat, text="Disciplinas/Materias")
        self.tabs.add(self.frame_planejar, text="Planejamento")
        self.tabs.add(self.frame_sessoes, text="Sessões")
        self.tabs.add(self.frame_tarefas, text="Tarefas")
        self.tabs.add(self.frame_graficos, text="Relatórios/Gráficos")
        self.tabs.add(self.frame_revisao, text="Revisão")
        self.tabs.add(self.frame_pomodoro, text="Pomodoro")

        # Atualiza combos/listas ao trocar de aba
        self.tabs.bind("<<NotebookTabChanged>>", self.on_tab_changed)

        self.after(800, self.check_revisoes)

    def on_tab_changed(self, event):
        tab = event.widget.tab(event.widget.select(), "text")
        # Atualiza combos/listas das guias conforme necessário
        if tab == "Sessões":
            self.frame_sessoes.refresh_combo_disc()
            self.frame_sessoes.refresh_sessoes()
        elif tab == "Disciplinas/Materias":
            self.frame_disc_mat.refresh_disciplinas()
            # Atualiza matérias da primeira disciplina, se houver
            items = self.frame_disc_mat.tree.get_children()
            if items:
                first_id = self.frame_disc_mat.tree.item(items[0])['values'][0]
                self.frame_disc_mat.refresh_materias(first_id)
            else:
                self.frame_disc_mat.refresh_materias(None)
        elif tab == "Planejamento":
            if hasattr(self.frame_planejar, "refresh"):
                self.frame_planejar.refresh()
        elif tab == "Tarefas":
            if hasattr(self.frame_tarefas, "refresh"):
                self.frame_tarefas.refresh()
        elif tab == "Relatórios/Gráficos":
            if hasattr(self.frame_graficos, "refresh"):
                self.frame_graficos.refresh()
        elif tab == "Revisão":
            if hasattr(self.frame_revisao, "refresh"):
                self.frame_revisao.refresh()

    def check_revisoes(self):
        from database import get_conn
        from datetime import date
        conn = get_conn()
        c = conn.cursor()
        hoje = date.today().isoformat()
        c.execute('''SELECT revisao.id, materia.nome, revisao.data_revisao
                     FROM revisao
                     JOIN materia ON materia.id = revisao.materia_id
                     WHERE revisao.realizada=0 AND revisao.data_revisao=?''', (hoje,))
        revisoes = c.fetchall()
        conn.close()
        if revisoes:
            materias = '\n'.join([f"{m} (Revisão {d})" for _, m, d in revisoes])
            messagebox.showinfo("Revisões Pendentes", f"Você tem revisões para hoje:\n\n{materias}")

if __name__ == "__main__":
    setup_db()
    app = App()
    app.mainloop()