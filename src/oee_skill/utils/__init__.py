def calculate_oee(availability: float, performance: float, quality: float) -> float:
    """Calcula OEE = Disponibilidade x Performance x Qualidade"""
    return (availability * performance * quality) / 1000000


def calculate_mttr(planned_hours: float, lost_units: int) -> float:
    """Calcula MTTR = Tempo Planejado / Numero de Paradas"""
    if lost_units > 0:
        return planned_hours / lost_units
    return 0


def calculate_mtbf(planned_hours: float, lost_units: int, total_production: int) -> float:
    """Calcula MTBF = (Tempo Planejado - Tempo de Parada) / Paradas"""
    if lost_units > 0 and total_production > 0:
        return planned_hours / lost_units
    return 0


def format_oee_label(machine: str, equipment_number: str = "", workstation: str = "", occurrence_type: str = "", action_to_avoid: str = "", register_date: str = "", release_date: str = "", responsible: str = "", lost_units: int = 0, total_production: int = 0, planned_hours: float = 0, availability: float = 0, performance: float = 0, quality: float = 0) -> str:
    """Formata label para ListBox"""
    oee = calculate_oee(availability, performance, quality)
    return f"{machine.ljust(15)} | {equipment_number.ljust(8)} | OEE: {oee:>7.2%}"


def calculate_status(oee: float) -> str:
    """Determina status based in OEE value"""
    if oee >= 0.85:
        return "excellent"
    elif oee >= 0.75:
        return "good"
    elif oee >= 0.60:
        return "regular"
    return "critical"