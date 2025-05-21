import sqlite3

DB = "controle_estudos.db"

def get_conn():
    return sqlite3.connect(DB)

def setup_db():
    conn = get_conn()
    c = conn.cursor()
    # Disciplinas
    c.execute("""
    CREATE TABLE IF NOT EXISTS disciplina (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL UNIQUE
    )""")
    # Materias
    c.execute("""
    CREATE TABLE IF NOT EXISTS materia (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        disciplina_id INTEGER,
        FOREIGN KEY(disciplina_id) REFERENCES disciplina(id)
    )""")
    # Planejamento
    c.execute("""
    CREATE TABLE IF NOT EXISTS planejamento (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        materia_id INTEGER,
        tipo TEXT,
        meta_minutos INTEGER,
        periodo_inicio DATE,
        periodo_fim DATE,
        FOREIGN KEY(materia_id) REFERENCES materia(id)
    )""")
    # Sessões de estudo
    c.execute("""
    CREATE TABLE IF NOT EXISTS sessao (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        materia_id INTEGER,
        data_inicio TEXT,
        data_fim TEXT,
        duracao INTEGER,
        tipo TEXT,
        anotacoes TEXT,
        disciplina_id INTEGER,
        FOREIGN KEY(materia_id) REFERENCES materia(id)
        FOREIGN KEY(disciplina_id) REFERENCES disciplina(id)
    )""")
    # Tarefas
    c.execute("""
    CREATE TABLE IF NOT EXISTS tarefa (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        materia_id INTEGER,
        titulo TEXT,
        prazo DATE,
        concluida INTEGER DEFAULT 0,
        tipo TEXT,
        FOREIGN KEY(materia_id) REFERENCES materia(id)
    )""")
    # Revisões
    c.execute("""
    CREATE TABLE IF NOT EXISTS revisao (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sessao_id INTEGER,
        materia_id INTEGER,
        data_revisao DATE,
        realizada INTEGER DEFAULT 0,
        FOREIGN KEY(sessao_id) REFERENCES sessao(id),
        FOREIGN KEY(materia_id) REFERENCES materia(id)
    )""")
    conn.commit()
    conn.close()