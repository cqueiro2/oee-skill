import os


class Config:
    """Configurações da aplicação"""
    
    def __init__(self):
        self.db_name = "factory_data.db"
        self.title_main = "SISTEMA OEE - VISAO GERAL"
        self.title_edit = "EDITAR EQUIPAMENTO"
        self.oee_colors = {
            "excellent": "G",
            "good": "G", 
            "regular": "Y",
            "poor": "R",
            "critical": "R"
        }
    
    def get_db_path(self) -> str:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_dir, self.db_name)


config = Config()