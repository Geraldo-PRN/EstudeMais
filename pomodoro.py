import threading
import time
from tkinter import messagebox

class PomodoroTimer:
    def __init__(self, label_status, get_study_time, get_pause_time):
        self.label_status = label_status
        self.get_study_time = get_study_time
        self.get_pause_time = get_pause_time
        self.timer_running = False

    def start(self):
        if self.timer_running:
            return
        try:
            study_minutes = int(self.get_study_time())
            pause_minutes = int(self.get_pause_time())
        except Exception:
            messagebox.showwarning("Pomodoro", "Informe tempos válidos.")
            return
        self.timer_running = True
        threading.Thread(target=self.run, args=(study_minutes, pause_minutes)).start()

    def run(self, study_minutes, pause_minutes):
        self.label_status.config(text="Estudo!")
        self.countdown(study_minutes * 60)
        self.label_status.config(text="Pausa!")
        messagebox.showinfo("Pomodoro", "Hora da pausa!")
        self.countdown(pause_minutes * 60)
        self.label_status.config(text="Ciclo Pomodoro finalizado!")
        messagebox.showinfo("Pomodoro", "Pomodoro completo!")
        self.timer_running = False

    def countdown(self, seconds):
        for t in range(seconds, 0, -1):
            mins, secs = divmod(t, 60)
            self.label_status.config(text=f"Tempo restante: {mins:02d}:{secs:02d}")
            time.sleep(1)
        self.label_status.config(text="00:00")