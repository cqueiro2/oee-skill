import os
import sys

base_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, base_path)

from asciimatics.scene import Scene
from asciimatics.screen import Screen
from config import config
from modules.database import Database
from modules.ui import ListFrame, EditFrame, GraphFrame, DashboardFrame


class OEESkill:
    def __init__(self):
        db_path = config.get_db_path()
        self.manager = Database(db_path)
        self.shared_data = {
            "id": None,
            "machine": "",
            "equipment_number": "",
            "workstation": "",
            "occurrence_type": "",
            "action_to_avoid": "",
            "register_date": "",
            "release_date": "",
            "responsible": "",
            "lost_units": "",
            "total_production": "",
            "planned_hours": "",
            "availability": "",
            "performance": "",
            "quality": ""
        }

    def run(self, screen):
        list_frame = ListFrame(screen, self.manager, self.shared_data)
        edit_frame = EditFrame(screen, self.manager, self.shared_data, list_frame)
        graph_frame = GraphFrame(screen, self.manager, self.shared_data, list_frame)
        dashboard_frame = DashboardFrame(screen, self.manager, self.shared_data, list_frame)
        
        scenes = [
            Scene([list_frame], -1, name="Main"),
            Scene([edit_frame], -1, name="Edit"),
            Scene([graph_frame], -1, name="Graph"),
            Scene([dashboard_frame], -1, name="Dashboard")
        ]
        
        screen.play(scenes, stop_on_resize=False, start_scene=scenes[0])

    def launch(self):
        Screen.wrapper(self.run)


def main():
    skill = OEESkill()
    skill.launch()


if __name__ == "__main__":
    main()