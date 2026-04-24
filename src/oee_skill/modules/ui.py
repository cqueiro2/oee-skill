import os
import sys
from datetime import datetime

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_PATH)

from asciimatics.widgets import Frame, ListBox, Layout, Divider, Button, Text, Label, TextBox, DropdownList
from asciimatics.widgets import Widget
from asciimatics.exceptions import NextScene, StopApplication
from utils import format_oee_label, calculate_oee, calculate_status, calculate_mttr, calculate_mtbf

DEFAULT_OEE = "OEE: 0.00%"
DEFAULT_STATUS = "STATUS: -"
DEFAULT_METRICS = "0.00h"

METRICAS = ['Disponibilidade', 'Performance', 'Qualidade', 'OEE']
BLOCO = chr(9608)


def draw_bar_graph(value: float, label: str = "", width: int = 30) -> str:
    """Desenha um gráfico de barra ASCII"""
    max_val = 100.0
    percent = min(max(value, 0), max_val)
    filled = int((percent / max_val) * width)
    bar = BLOCO * filled + "░" * (width - filled)
    return f"{label:<15} [{bar}] {percent:>5.1f}%"


def draw_colored_bar(value: float, label: str = "", width: int = 30) -> str:
    """Desenha gráfico com indicador de status"""
    max_val = 100.0
    percent = min(max(value, 0), max_val)
    filled = int((percent / max_val) * width)
    
    if percent >= 85:
        indicador = "[OK] "
    elif percent >= 60:
        indicador = "[!!] "
    else:
        indicador = "[!]"
    
    bar = BLOCO * filled + "░" * (width - filled)
    return f"{label:<15} {indicador:<4} [{bar}] {percent:>5.1f}%"


class ListFrame(Frame):
    def __init__(self, screen, manager, data):
        super().__init__(screen, screen.height, screen.width, data=data, title="SISTEMA OEE - DASHBOARD")
        self.manager = manager
        self._pending_edit_id = None  # ID do registro a ser editado

        # Layout principal: 50% Lista, 50% Detalhes
        layout = Layout([50, 50], fill_frame=True)
        self.add_layout(layout)

        # Coluna da Esquerda: Lista
        self._list = ListBox(Widget.FILL_FRAME, self._get_options(), name="selection", on_change=self._on_select)
        layout.add_widget(self._list, 0)

        # Coluna da Direita: Detalhes
        self._details_label = Label("DETALHES DO REGISTRO", align="^")
        layout.add_widget(self._details_label, 1)
        layout.add_widget(Divider(), 1)

        self._detail_widgets = {}
        fields = [
            ("Maquina", "machine"),
            ("Equipamento", "equipment_number"),
            ("Estacao", "workstation"),
            ("Responsavel", "responsible"),
            ("Data Registro", "register_date"),
            ("Prev. Liberacao", "release_date"),
            ("Tipo Ocorrencia", "occurrence_type"),
            ("Acao p/ Evitar", "action_to_avoid"),
            ("Horas Plan.", "planned_hours"),
            ("Prod. Total", "total_production"),
            ("Un. Perdidas", "lost_units"),
            ("Disponibilidade", "availability"),
            ("Performance", "performance"),
            ("Qualidade", "quality"),
        ]

        for lbl, key in fields:
            w = Label(f"{lbl}: -")
            self._detail_widgets[key] = w
            layout.add_widget(w, 1)

        layout.add_widget(Divider(), 1)
        self._oee_dashboard = Label("OEE GLOBAL: 0.00%", align="^")
        layout.add_widget(self._oee_dashboard, 1)

        # Botoes na parte inferior
        layout.add_widget(Divider(), 0)
        buttons = Layout([1, 1, 1, 1, 1])
        self.add_layout(buttons)
        buttons.add_widget(Button("Novo", self._add), 0)
        buttons.add_widget(Button("Editar", self._edit), 1)
        buttons.add_widget(Button("Excluir", self._delete), 2)
        buttons.add_widget(Button("Grafico", self._graph), 3)
        buttons.add_widget(Button("Sair", self._quit), 4)

        self.fix()
        self._on_select()

    def _on_select(self):
        if self._list.value is None:
            return

        rec = self.manager.get_by_id(self._list.value)
        if rec:
            data_map = {
                "machine": rec[1], "equipment_number": rec[2], "workstation": rec[3],
                "occurrence_type": rec[4], "action_to_avoid": rec[5], "register_date": rec[6],
                "release_date": rec[7], "responsible": rec[8], "lost_units": str(rec[9]),
                "total_production": str(rec[10]), "planned_hours": str(rec[11]),
                "availability": f"{rec[12]}%", "performance": f"{rec[13]}%", "quality": f"{rec[14]}%"
            }

            for key, val in data_map.items():
                if key in self._detail_widgets:
                    lbl = key.replace("_", " ").title()
                    self._detail_widgets[key].text = f"{lbl}: {val}"

            oee = calculate_oee(rec[12], rec[13], rec[14])
            self._oee_dashboard.text = f"OEE GLOBAL: {oee:.2%}"

    def reset(self):
        super().reset()
        self._list.options = self._get_options()
        self._on_select()

    def _get_options(self):
        records = self.manager.get_all()
        if not records:
            return []
        return [
            (format_oee_label(r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9], r[10], r[11], r[12], r[13], r[14]), r[0])
            for r in records
        ]

    def _clear_data(self):
        self.data["id"] = None
        self.data["machine"] = ""
        self.data["equipment_number"] = ""
        self.data["workstation"] = ""
        self.data["occurrence_type"] = ""
        self.data["action_to_avoid"] = ""
        self.data["register_date"] = datetime.now().strftime("%d/%m/%Y")
        self.data["release_date"] = ""
        self.data["responsible"] = ""
        self.data["lost_units"] = ""
        self.data["total_production"] = ""
        self.data["planned_hours"] = ""
        self.data["availability"] = ""
        self.data["performance"] = ""
        self.data["quality"] = ""

    def _add(self):
        self._clear_data()
        raise NextScene("Edit")

    def _edit(self):
        if self._list.value is None:
            return
        # Armazena o ID como atributo do objeto (nao no dict que é copiado)
        self._pending_edit_id = self._list.value
        raise NextScene("Edit")

    def _delete(self):
        if self._list.value is None:
            return
        self.manager.delete(self._list.value)
        self.update_list()

    def _quit(self):
        raise StopApplication("Fim")

    def _graph(self):
        raise NextScene("Graph")

    def update_list(self):
        self._list.options = self._get_options()


class EditFrame(Frame):
    def __init__(self, screen, manager, data, list_frame):
        super().__init__(screen, 26, 72, data=data, title="CADASTRO DE EQUIPAMENTO", can_scroll=False)
        self.manager = manager
        self._list_frame = list_frame

        self._oee_label    = Label(DEFAULT_OEE)
        self._status_label = Label(DEFAULT_STATUS)
        self._mttr_label   = Label(f"MTTR: {DEFAULT_METRICS}")
        self._mtbf_label   = Label(f"MTBF: {DEFAULT_METRICS}")

        # --- Filtro de registros ---
        layout0 = Layout([100])
        self.add_layout(layout0)
        self._dropdown = DropdownList(
            self._get_machine_options(),
            label="Filtrar Maquina:",
            name="filter_machine",
            on_change=self._on_filter_select,
        )
        layout0.add_widget(self._dropdown)
        layout0.add_widget(Divider())

        # --- Campos do formulario ---
        layout = Layout([100])
        self.add_layout(layout)
        layout.add_widget(Text("Maquina:", "machine"))
        layout.add_widget(Text("Numero Equipamento:", "equipment_number"))
        layout.add_widget(Text("Estacao de Trabalho:", "workstation"))
        layout.add_widget(Text("Data Registro:", "register_date"))
        layout.add_widget(Divider())

        layout2 = Layout([100])
        self.add_layout(layout2)
        layout2.add_widget(Text("Tipo da Ocorrencia:", "occurrence_type"))

        layout3 = Layout([100])
        self.add_layout(layout3)
        layout3.add_widget(Text("Acao para Evitar:", "action_to_avoid"))
        layout3.add_widget(Text("Data Prevista Lib.:", "release_date"))
        layout3.add_widget(Text("Responsavel:", "responsible"))
        layout3.add_widget(Divider())

        layout4 = Layout([1, 1, 1])
        self.add_layout(layout4)
        layout4.add_widget(Text("Horas Plan:",    "planned_hours",    on_change=self._update_oee), 0)
        layout4.add_widget(Text("Un. Perdidas:",  "lost_units",       on_change=self._update_oee), 1)
        layout4.add_widget(Text("Prod. Total:",   "total_production", on_change=self._update_oee), 2)

        layout5 = Layout([1, 1, 1])
        self.add_layout(layout5)
        layout5.add_widget(Text("Disponib. (%):", "availability", on_change=self._update_oee), 0)
        layout5.add_widget(Text("Performance (%):","performance", on_change=self._update_oee), 1)
        layout5.add_widget(Text("Qualidade (%):", "quality",      on_change=self._update_oee), 2)

        layout6 = Layout([1, 1, 1, 1])
        self.add_layout(layout6)
        layout6.add_widget(self._oee_label,    0)
        layout6.add_widget(self._status_label, 1)
        layout6.add_widget(self._mttr_label,   2)
        layout6.add_widget(self._mtbf_label,   3)

        buttons = Layout([1, 1, 1])
        self.add_layout(buttons)
        buttons.add_widget(Button("Novo",   self._new),    0)
        buttons.add_widget(Button("Salvar", self._save),   1)
        buttons.add_widget(Button("Voltar", self._cancel), 2)
        self.fix()

    def _get_machine_options(self):
        """Retorna opcoes para o DropdownList com todos os registros do banco."""
        records = self.manager.get_all()
        options = [("-- Novo Registro --", None)]
        for rec in records:
            label = f"{rec[1]} | {rec[2]} | {rec[3]}"
            options.append((label[:60], rec[0]))
        return options

    def _on_filter_select(self):
        """Carrega o registro selecionado no dropdown para os campos do formulario."""
        if getattr(self, "_resetting", False):
            return
        self.save()
        selected_id = self.data.get("filter_machine")
        if selected_id is None:
            # Novo registro - limpar campos
            self._clear_fields()
        else:
            rec = self.manager.get_by_id(selected_id)
            if rec:
                self._load_rec(rec)
        self._update_oee()

    def _load_rec(self, rec):
        """Carrega um registro (tupla do banco) nos campos do formulario."""
        self.data["id"]               = rec[0]
        self.data["machine"]          = rec[1]
        self.data["equipment_number"] = rec[2] or ""
        self.data["workstation"]      = rec[3] or ""
        self.data["occurrence_type"]  = rec[4] or ""
        self.data["action_to_avoid"]  = rec[5] or ""
        self.data["register_date"]    = rec[6] or ""
        self.data["release_date"]     = rec[7] or ""
        self.data["responsible"]      = str(rec[8] or "")
        self.data["lost_units"]       = str(rec[9] or "")
        self.data["total_production"] = str(rec[10] or "")
        self.data["planned_hours"]    = str(rec[11] or "")
        self.data["availability"]     = str(rec[12])
        self.data["performance"]      = str(rec[13])
        self.data["quality"]          = str(rec[14])
        # Recarregar widgets com os novos dados
        super().reset()

    def _clear_fields(self):
        """Limpa todos os campos para um novo cadastro."""
        self.data["id"] = None
        for key in ["machine", "equipment_number", "workstation", "occurrence_type",
                    "action_to_avoid", "register_date", "release_date", "responsible",
                    "lost_units", "total_production", "planned_hours",
                    "availability", "performance", "quality"]:
            self.data[key] = ""
        super().reset()

    def reset(self):
        self._resetting = True
        # Atualizar opcoes do dropdown com registros atuais
        self._dropdown.options = self._get_machine_options()
        # Pre-selecionar o registro sendo editado no dropdown
        pending_id = getattr(self._list_frame, "_pending_edit_id", None)
        if pending_id is not None:
            self.data["filter_machine"] = pending_id
            rec = self.manager.get_by_id(pending_id)
            if rec:
                self.data["id"]               = rec[0]
                self.data["machine"]          = rec[1]
                self.data["equipment_number"] = rec[2] or ""
                self.data["workstation"]      = rec[3] or ""
                self.data["occurrence_type"]  = rec[4] or ""
                self.data["action_to_avoid"]  = rec[5] or ""
                self.data["register_date"]    = rec[6] or ""
                self.data["release_date"]     = rec[7] or ""
                self.data["responsible"]      = str(rec[8] or "")
                self.data["lost_units"]       = str(rec[9] or "")
                self.data["total_production"] = str(rec[10] or "")
                self.data["planned_hours"]    = str(rec[11] or "")
                self.data["availability"]     = str(rec[12])
                self.data["performance"]      = str(rec[13])
                self.data["quality"]          = str(rec[14])
        else:
            self.data["filter_machine"] = None
            self.data["id"] = None
            for key in ["machine", "equipment_number", "workstation", "occurrence_type",
                        "action_to_avoid", "register_date", "release_date", "responsible",
                        "lost_units", "total_production", "planned_hours",
                        "availability", "performance", "quality"]:
                self.data[key] = ""
        super().reset()
        self._resetting = False
        self._update_oee()

    def _update_oee(self):

        if getattr(self, "_resetting", False):
            return
        try:
            self.save()
            availability = float(self.data["availability"] or 0)
            performance = float(self.data["performance"] or 0)
            quality = float(self.data["quality"] or 0)
            planned_hours = float(self.data["planned_hours"] or 0)
            lost_units = int(self.data["lost_units"] or 0)
            total_production = int(self.data["total_production"] or 0)

            oee = calculate_oee(availability, performance, quality)
            status = calculate_status(oee)
            mttr = calculate_mttr(planned_hours, lost_units)
            mtbf = calculate_mtbf(planned_hours, lost_units, total_production)

            self._oee_label.text = f"OEE: {oee:.2%}"
            self._status_label.text = f"STATUS: {status.upper()}"
            self._mttr_label.text = f"MTTR: {mttr:.2f}h"
            self._mtbf_label.text = f"MTBF: {mtbf:.2f}h"
        except ValueError:
            self._oee_label.text = "OEE: ERRO"
            self._status_label.text = DEFAULT_STATUS
            self._mttr_label.text = f"MTTR: {DEFAULT_METRICS}"
            self._mtbf_label.text = f"MTBF: {DEFAULT_METRICS}"

    def _new(self):
        """Limpa campos para cadastrar um novo registro."""
        self._list_frame._pending_edit_id = None
        self._clear_fields()
        self._update_oee()

    def _save(self):
        self.save()
        data = self.data

        record_id = data.get("id")
        machine = data.get("machine", "").strip()
        if not machine:
            return

        values = {
            "machine": machine,
            "equipment_number": data.get("equipment_number", "").strip(),
            "workstation": data.get("workstation", "").strip(),
            "occurrence_type": data.get("occurrence_type", "").strip(),
            "action_to_avoid": data.get("action_to_avoid", "").strip(),
            "register_date": data.get("register_date", "").strip() or datetime.now().strftime("%d/%m/%Y"),
            "release_date": data.get("release_date", "").strip(),
            "responsible": data.get("responsible", "").strip(),
            "lost_units": int(data.get("lost_units") or 0),
            "total_production": int(data.get("total_production") or 0),
            "planned_hours": float(data.get("planned_hours") or 0),
            "availability": float(data.get("availability") or 0),
            "performance": float(data.get("performance") or 0),
            "quality": float(data.get("quality") or 0),
        }

        if record_id is None:
            self.manager.insert(**values)
        else:
            self.manager.update(int(record_id), **values)

        if self._list_frame:
            self._list_frame.update_list()

        raise NextScene("Main")

    def _cancel(self):
        raise NextScene("Main")


class GraphFrame(Frame):
    def __init__(self, screen, manager, data, list_frame):
        super().__init__(screen, screen.height, screen.width, data=data,
                         title="DASHBOARD OEE - GRAFICOS", can_scroll=False)
        self.manager = manager
        self._list_frame = list_frame

        # TextBox: suporta multiplas linhas e rolagem nativa
        self._chart_view = TextBox(Widget.FILL_FRAME, readonly=True, name="chart_view")

        layout = Layout([100], fill_frame=True)
        self.add_layout(layout)
        layout.add_widget(self._chart_view)

        buttons = Layout([1, 1])
        self.add_layout(buttons)
        buttons.add_widget(Button("Voltar", self._go_main), 0)
        buttons.add_widget(Button("Atualizar", self._refresh), 1)
        self.fix()

        self._update_charts()

    def _refresh(self):
        self._update_charts()

    def _go_main(self):
        raise NextScene("Main")

    def _update_charts(self):
        records = self.manager.get_all()

        SEP  = "=" * 68
        THIN = "-" * 68

        lines = []
        lines.append(SEP)
        lines.append("      DASHBOARD OEE - GRAFICOS DE PERFORMANCE")
        lines.append(SEP)
        lines.append(f'{"Metrica":<16} {"Status":<6} {"Grafico":<32} {"Valor":>6}')
        lines.append(THIN)

        if records:
            t_avail = t_perf = t_qual = t_oee = count = 0

            for rec in records:
                machine     = str(rec[1])[:15]
                availability = float(rec[12] or 0)
                performance  = float(rec[13] or 0)
                quality      = float(rec[14] or 0)
                oee          = calculate_oee(availability, performance, quality) * 100

                t_avail += availability
                t_perf  += performance
                t_qual  += quality
                t_oee   += oee
                count   += 1

                lines.append(f">> {machine}")
                lines.append(draw_colored_bar(availability, "  Disponib."))
                lines.append(draw_colored_bar(performance,  "  Performan."))
                lines.append(draw_colored_bar(quality,      "  Qualidade"))
                lines.append(draw_colored_bar(oee,          "  OEE"))
                lines.append(THIN)

            if count > 0:
                avg_avail = t_avail / count
                avg_perf  = t_perf  / count
                avg_qual  = t_qual  / count
                avg_oee   = t_oee   / count

                lines.append("")
                lines.append(SEP)
                lines.append("      MEDIAS GERAIS DA FABRICA")
                lines.append(SEP)
                lines.append(draw_colored_bar(avg_avail, "Disponib."))
                lines.append(draw_colored_bar(avg_perf,  "Performance"))
                lines.append(draw_colored_bar(avg_qual,  "Qualidade"))
                lines.append(draw_colored_bar(avg_oee,   "OEE Medio"))
                lines.append(SEP)
        else:
            lines.append("  Nenhum dado cadastrado.")
            lines.append(SEP)

        # TextBox.value recebe lista de strings (uma por linha)
        self._chart_view.value = lines
