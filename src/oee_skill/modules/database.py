import sqlite3
import os


class Database:
    """Gerenciamento de dados OEE"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._create_table()
        self._migrate_if_needed()

    def _create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS oee_metrics (
                id INTEGER PRIMARY KEY,
                machine TEXT,
                equipment_number TEXT,
                workstation TEXT,
                occurrence_type TEXT,
                action_to_avoid TEXT,
                register_date TEXT,
                release_date TEXT,
                responsible TEXT,
                lost_units INTEGER,
                total_production INTEGER,
                planned_hours REAL,
                availability REAL,
                performance REAL,
                quality REAL
            )
        ''')
        self.conn.commit()

    def _migrate_if_needed(self):
        try:
            self.cursor.execute("PRAGMA table_info(oee_metrics)")
            columns = [col[1] for col in self.cursor.fetchall()]
            
            if len(columns) < 15:
                self.cursor.execute("DROP TABLE IF EXISTS oee_metrics")
                self._create_table()
                self.conn.commit()
        except sqlite3.OperationalError:
            self._create_table()

    def get_all(self):
        self.cursor.execute(
            "SELECT id, machine, equipment_number, workstation, occurrence_type, action_to_avoid, register_date, release_date, responsible, lost_units, total_production, planned_hours, availability, performance, quality FROM oee_metrics"
        )
        return self.cursor.fetchall()

    def get_by_id(self, uid: int):
        self.cursor.execute("SELECT * FROM oee_metrics WHERE id=?", (uid,))
        return self.cursor.fetchone()

    def insert(self, machine: str, equipment_number: str, workstation: str, occurrence_type: str, action_to_avoid: str, register_date: str, release_date: str, responsible: str, lost_units: int, total_production: int, planned_hours: float, availability: float, performance: float, quality: float):
        self.cursor.execute(
            "INSERT INTO oee_metrics (machine, equipment_number, workstation, occurrence_type, action_to_avoid, register_date, release_date, responsible, lost_units, total_production, planned_hours, availability, performance, quality) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (machine, equipment_number, workstation, occurrence_type, action_to_avoid, register_date, release_date, responsible, lost_units, total_production, planned_hours, availability, performance, quality)
        )
        self.conn.commit()
        return self.cursor.lastrowid

    def update(self, uid: int, machine: str, equipment_number: str, workstation: str, occurrence_type: str, action_to_avoid: str, register_date: str, release_date: str, responsible: str, lost_units: int, total_production: int, planned_hours: float, availability: float, performance: float, quality: float):
        self.cursor.execute(
            "UPDATE oee_metrics SET machine=?, equipment_number=?, workstation=?, occurrence_type=?, action_to_avoid=?, register_date=?, release_date=?, responsible=?, lost_units=?, total_production=?, planned_hours=?, availability=?, performance=?, quality=? WHERE id=?",
            (machine, equipment_number, workstation, occurrence_type, action_to_avoid, register_date, release_date, responsible, lost_units, total_production, planned_hours, availability, performance, quality, uid)
        )
        self.conn.commit()

    def delete(self, uid: int):
        self.cursor.execute("DELETE FROM oee_metrics WHERE id=?", (uid,))
        self.conn.commit()

    def close(self):
        self.conn.close()