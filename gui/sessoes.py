import tkinter as tk
from tkinter import ttk, messagebox
from database import get_conn
from datetime import datetime, timedelta, date

class Cronometro:
    def __init__(self, label, tempo_callback):
        self.label = label
        self.tempo_callback = tempo_callback
        self.running = False
        self.paused = False
        self.start_time = None
        self.elapsed = timedelta()
        self._job = None

    def _update(self):
        if self.running and not self.paused:
            now = datetime.now()
            self.elapsed = now - self.start_time
            tempo_str = str(self.elapsed).split(".")[0]
            # Pad with leading zero if needed (H:MM:SS -> HH:MM:SS)
            if len(tempo_str) == 7:
                tempo_str = "0" + tempo_str
            self.label.config(text=tempo_str)
            self._job = self.label.after(1000, self._update)

    def play(self):
        if not self.running:
            self.start_time = datetime.now()
            self.elapsed = timedelta()
            self.running = True
            self.paused = False
            self._update()
        elif self.paused:
            self.start_time = datetime.now() - self.elapsed
            self.paused = False
            self._update()

    def pause(self):
        if self.running and not self.paused:
            self.paused = True
            if self._job:
                self.label.after_cancel(self._job)

    def stop(self):
        if self.running:
            if not self.paused and self._job:
                self.label.after_cancel(self._job)
            tempo_str = str(self.elapsed).split(".")[0]
            if len(tempo_str) == 7:
                tempo_str = "0" + tempo_str
            self.tempo_callback(tempo_str)
            self.label.config(text="00:00:00")
            self.running = False
            self.paused = False
            self.elapsed = timedelta()
            self._job = None

class SessoesFrame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.frame_revisao = None  # Referência para o frame de revisão (será setada pelo main)
        self.build()

    def build(self):
        tk.Label(self, text="Registro de Sessão", font=("Arial", 13)).place(x=10, y=10)

        # Disciplinas
        tk.Label(self, text="Disciplina:").place(x=10, y=50)
        self.combo_disc = ttk.Combobox(self, state="readonly")
        self.combo_disc.place(x=80, y=50, width=200)
        self.combo_disc.bind("<<ComboboxSelected>>", self.on_disciplina_select)
        self.refresh_combo_disc()

        # Matérias
        tk.Label(self, text="Matéria:").place(x=300, y=50)
        self.combo_mat = ttk.Combobox(self, state="readonly")
        self.combo_mat.place(x=360, y=50, width=200)

        # Data atual (DD/MM/AAAA)
        tk.Label(self, text="Data:").place(x=600, y=50)
        self.var_data = tk.StringVar()
        self.var_data.set(date.today().strftime("%d/%m/%Y"))
        self.entry_data = tk.Entry(self, textvariable=self.var_data, width=12)
        self.entry_data.place(x=640, y=50)

        # Tipo de sessão
        tk.Label(self, text="Tipo:").place(x=10, y=90)
        self.combo_tipo = ttk.Combobox(self, values=["estudo", "revisao", "exercicio"], state="readonly")
        self.combo_tipo.place(x=60, y=90, width=120)

        # Tempo (HH:MM:SS)
        tk.Label(self, text="Tempo (HH:MM:SS):").place(x=200, y=90)
        self.entry_tempo = tk.Entry(self)
        self.entry_tempo.place(x=340, y=90, width=80)
        self.entry_tempo.insert(0, "00:25:00")

        # Cronômetro/Pomodoro
        tk.Label(self, text="Cronômetro:").place(x=440, y=90)
        self.lbl_cronometro = tk.Label(self, text="00:00:00", fg="darkblue", font=("Arial", 12, "bold"))
        self.lbl_cronometro.place(x=530, y=90)
        self.cronometro = Cronometro(self.lbl_cronometro, self.set_tempo_from_cronometro)
        tk.Button(self, text="Play", command=self.cronometro.play).place(x=640, y=88)
        tk.Button(self, text="Pause", command=self.cronometro.pause).place(x=690, y=88)
        tk.Button(self, text="Finalizar", command=self.cronometro.stop).place(x=750, y=88)

        # Anotações
        tk.Label(self, text="Anotações:").place(x=10, y=130)
        self.entry_anot = tk.Entry(self)
        self.entry_anot.place(x=90, y=130, width=300)

        # Agendar Revisão
        tk.Label(self, text="Agendar Revisão:").place(x=410, y=130)
        self.combo_revisao = ttk.Combobox(self, values=["", "7", "15", "30", "45", "60"], state="readonly")
        self.combo_revisao.place(x=530, y=130, width=60)
        tk.Button(self, text="Registrar Sessão", command=self.add_sessao).place(x=600, y=128)

        # Sessões registradas
        self.tree = ttk.Treeview(self, columns=("Disciplina", "Materia", "Tipo", "Data", "Tempo", "Anotacoes"), show="headings")
        self.tree.place(x=10, y=170, width=900, height=220)
        for col in ["Disciplina", "Materia", "Tipo", "Data", "Tempo", "Anotacoes"]:
            self.tree.heading(col, text=col)
        self.refresh_sessoes()

    def set_tempo_from_cronometro(self, tempo_str):
        self.entry_tempo.delete(0, tk.END)
        self.entry_tempo.insert(0, tempo_str)

    def refresh_combo_disc(self):
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT id, nome FROM disciplina")
        self.disciplinas = c.fetchall()
        self.combo_disc['values'] = [f"{id}: {nome}" for id, nome in self.disciplinas]
        conn.close()

    def on_disciplina_select(self, event):
        sel = self.combo_disc.get()
        if sel:
            disc_id = int(sel.split(":")[0])
            conn = get_conn()
            c = conn.cursor()
            c.execute("SELECT id, nome FROM materia WHERE disciplina_id=?", (disc_id,))
            mats = c.fetchall()
            self.combo_mat['values'] = [f"{id}: {nome}" for id, nome in mats]
            self.combo_mat.set("")  # Limpa seleção anterior
            conn.close()

    def validar_tempo(self, tempo_str):
        try:
            h, m, s = map(int, tempo_str.split(":"))
            return h >= 0 and m >= 0 and s >= 0 and m < 60 and s < 60
        except Exception:
            return False

    def tempo_para_minutos(self, tempo_str):
        h, m, s = map(int, tempo_str.split(":"))
        return h*60 + m + s/60

    def data_ddmmaaaa_para_iso(self, data_str):
        # De "DD/MM/AAAA" para "YYYY-MM-DD"
        try:
            d = datetime.strptime(data_str, "%d/%m/%Y")
            return d.strftime("%Y-%m-%d")
        except Exception:
            return date.today().isoformat()

    def add_sessao(self):
        mat_sel = self.combo_mat.get()
        disc_sel = self.combo_disc.get()
        tipo = self.combo_tipo.get()
        data_sessao = self.entry_data.get()
        tempo_str = self.entry_tempo.get().strip()
        anot = self.entry_anot.get().strip()
        revisar = self.combo_revisao.get()
        if not (mat_sel and disc_sel and tipo and tempo_str and data_sessao):
            messagebox.showwarning("Sessão", "Preencha todos os campos obrigatórios.")
            return
        if not self.validar_tempo(tempo_str):
            messagebox.showwarning("Tempo inválido", "Informe o tempo no formato HH:MM:SS!")
            return
        materia_id = int(mat_sel.split(":")[0])
        disciplina_id = int(disc_sel.split(":")[0])
        dur = int(self.tempo_para_minutos(tempo_str))
        # O campo "data_inicio" será data + 00:00, "data_fim" = data + tempo
        data_inicio = f"{self.data_ddmmaaaa_para_iso(data_sessao)} 00:00"
        try:
            dt_inicio = datetime.strptime(data_inicio, "%Y-%m-%d %H:%M")
            dt_fim = dt_inicio + timedelta(minutes=dur)
            data_fim = dt_fim.strftime("%Y-%m-%d %H:%M")
        except Exception:
            data_fim = data_inicio
        conn = get_conn()
        c = conn.cursor()
        c.execute('''INSERT INTO sessao (materia_id, disciplina_id, data_inicio, data_fim, duracao, tipo, anotacoes)
                     VALUES (?,?,?,?,?,?,?)''', (materia_id, disciplina_id, data_inicio, data_fim, dur, tipo, anot))
        sessao_id = c.lastrowid
        conn.commit()
        # Revisão
        if revisar and revisar.isdigit():
            dias = int(revisar)
            dt_revisao = datetime.strptime(self.data_ddmmaaaa_para_iso(data_sessao), "%Y-%m-%d") + timedelta(days=dias)
            data_revisao = dt_revisao.strftime("%Y-%m-%d")
            c.execute('''INSERT INTO revisao (sessao_id, materia_id, data_revisao)
                         VALUES (?,?,?)''', (sessao_id, materia_id, data_revisao))
            conn.commit()
        conn.close()
        self.entry_tempo.delete(0, tk.END)
        self.entry_tempo.insert(0, "00:25:00")
        self.entry_anot.delete(0, tk.END)
        self.combo_tipo.set("")
        self.combo_mat.set("")
        self.combo_disc.set("")
        self.combo_revisao.set("")
        self.refresh_sessoes()

    def refresh_sessoes(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        conn = get_conn()
        c = conn.cursor()
        # Agora também traz o nome da disciplina
        c.execute('''
            SELECT d.nome, m.nome, s.tipo, date(s.data_inicio), s.duracao, s.anotacoes
            FROM sessao s
            JOIN materia m ON m.id = s.materia_id
            JOIN disciplina d ON d.id = s.disciplina_id
            ORDER BY s.data_inicio DESC
        ''')
        for disc_nome, mat_nome, tipo, data_inicio, dur, anot in c.fetchall():
            # data_inicio está em ISO, converte para DD/MM/AAAA
            try:
                data_fmt = datetime.strptime(data_inicio, "%Y-%m-%d").strftime("%d/%m/%Y")
            except Exception:
                data_fmt = data_inicio
            h = dur // 60
            m = dur % 60
            s = 0
            tempo_fmt = f"{int(h):02d}:{int(m):02d}:{int(s):02d}"
            self.tree.insert('', 'end', values=(disc_nome, mat_nome, tipo, data_fmt, tempo_fmt, anot))
        # Atualiza revisão em tempo real se houver referência
        if hasattr(self, "frame_revisao") and self.frame_revisao is not None:
            if hasattr(self.frame_revisao, "refresh"):
                self.frame_revisao.refresh()
        conn.close()