import sqlite3


COLUMNS = (
    "id, machine, equipment_number, workstation, occurrence_type, action_to_avoid, "
    "register_date, release_date, responsible, lost_units, total_production, "
    "planned_hours, availability, performance, quality"
)

INSERT_COLS = (
    "machine, equipment_number, workstation, occurrence_type, action_to_avoid, "
    "register_date, release_date, responsible, lost_units, total_production, "
    "planned_hours, availability, performance, quality"
)

PLACEHOLDERS = "?,?,?,?,?,?,?,?,?,?,?,?,?,?"

CREATE_SQL = '''
    CREATE TABLE IF NOT EXISTS oee_metrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        machine TEXT NOT NULL,
        equipment_number TEXT DEFAULT "",
        workstation TEXT DEFAULT "",
        occurrence_type TEXT DEFAULT "",
        action_to_avoid TEXT DEFAULT "",
        register_date TEXT DEFAULT "",
        release_date TEXT DEFAULT "",
        responsible TEXT DEFAULT "",
        lost_units INTEGER DEFAULT 0,
        total_production INTEGER DEFAULT 0,
        planned_hours REAL DEFAULT 0,
        availability REAL DEFAULT 0,
        performance REAL DEFAULT 0,
        quality REAL DEFAULT 0
    )
'''


class Database:
    """Gerenciamento de dados OEE"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()

    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._connect() as conn:
            conn.execute(CREATE_SQL)
            conn.commit()
            self._migrate_if_needed(conn)
            self._seed_data(conn)

    def _migrate_if_needed(self, conn):
        cursor = conn.execute("PRAGMA table_info(oee_metrics)")
        columns = [col[1] for col in cursor.fetchall()]
        if len(columns) < 15:
            conn.execute("DROP TABLE IF EXISTS oee_metrics")
            conn.execute(CREATE_SQL.replace("IF NOT EXISTS", ""))
            conn.commit()

    def _seed_data(self, conn):
        count = conn.execute("SELECT COUNT(*) FROM oee_metrics").fetchone()[0]
        if count == 0:
            seed = [
                ("Torno CNC 01", "EQP-001", "Estacao 1", "Quebra de ferramenta",
                 "Verificar diariamente", "10/01/2024", "15/01/2024", "Joao Silva",
                 2, 100, 8.0, 85.0, 90.0, 95.0),
                ("Fresadora 02", "EQP-002", "Estacao 2", "Desgaste anormal",
                 "Troca preventiva", "11/01/2024", "18/01/2024", "Maria Santos",
                 1, 150, 8.0, 92.0, 88.0, 98.0),
                ("Prensa 03", "EQP-003", "Estacao 3", "Superaquecimento",
                 "Limpar ventiladores", "12/01/2024", "20/01/2024", "Pedro Costa",
                 3, 200, 8.0, 78.0, 85.0, 92.0),
            ]
            conn.executemany(
                f"INSERT INTO oee_metrics ({INSERT_COLS}) VALUES ({PLACEHOLDERS})",
                seed
            )
            conn.commit()

    def get_all(self):
        with self._connect() as conn:
            rows = conn.execute(
                f"SELECT {COLUMNS} FROM oee_metrics ORDER BY id"
            ).fetchall()
            return [tuple(r) for r in rows]

    def get_by_id(self, uid: int):
        with self._connect() as conn:
            row = conn.execute(
                f"SELECT {COLUMNS} FROM oee_metrics WHERE id=?", (uid,)
            ).fetchone()
            return tuple(row) if row else None

    def insert(self, machine, equipment_number, workstation, occurrence_type,
               action_to_avoid, register_date, release_date, responsible,
               lost_units, total_production, planned_hours,
               availability, performance, quality):
        with self._connect() as conn:
            cursor = conn.execute(
                f"INSERT INTO oee_metrics ({INSERT_COLS}) VALUES ({PLACEHOLDERS})",
                (machine, equipment_number, workstation, occurrence_type,
                 action_to_avoid, register_date, release_date, responsible,
                 lost_units, total_production, planned_hours,
                 availability, performance, quality)
            )
            conn.commit()
            return cursor.lastrowid

    def update(self, uid, machine, equipment_number, workstation, occurrence_type,
               action_to_avoid, register_date, release_date, responsible,
               lost_units, total_production, planned_hours,
               availability, performance, quality):
        with self._connect() as conn:
            conn.execute(
                f"""UPDATE oee_metrics SET
                    machine=?, equipment_number=?, workstation=?,
                    occurrence_type=?, action_to_avoid=?,
                    register_date=?, release_date=?, responsible=?,
                    lost_units=?, total_production=?, planned_hours=?,
                    availability=?, performance=?, quality=?
                WHERE id=?""",
                (machine, equipment_number, workstation, occurrence_type,
                 action_to_avoid, register_date, release_date, responsible,
                 lost_units, total_production, planned_hours,
                 availability, performance, quality, uid)
            )
            conn.commit()

    def delete(self, uid: int):
        with self._connect() as conn:
            conn.execute("DELETE FROM oee_metrics WHERE id=?", (uid,))
            conn.commit()

    def close(self):
        pass  # conexoes fechadas automaticamente pelo context manager