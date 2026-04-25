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
VERDE = chr(9607)
AMARELO = chr(9607)
VERMELHO = chr(9607)


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
        indicador ="[ ! ] "
    
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
        buttons = Layout([1, 1, 1, 1, 1, 1])
        self.add_layout(buttons)
        buttons.add_widget(Button("Novo", self._add), 0)
        buttons.add_widget(Button("Editar", self._edit), 1)
        buttons.add_widget(Button("Excluir", self._delete), 2)
        buttons.add_widget(Button("Grafico", self._graph), 3)
        buttons.add_widget(Button("Dashboard", self._dashboard), 4)
        buttons.add_widget(Button("Sair", self._quit), 5)

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

    def _dashboard(self):
        raise NextScene("Dashboard")

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

    # Lista de campos editaveis (na ordem dos indices do banco)
    _FIELD_MAP = [
        (1,  "machine"),
        (2,  "equipment_number"),
        (3,  "workstation"),
        (4,  "occurrence_type"),
        (5,  "action_to_avoid"),
        (6,  "register_date"),
        (7,  "release_date"),
        (8,  "responsible"),
        (9,  "lost_units"),
        (10, "total_production"),
        (11, "planned_hours"),
        (12, "availability"),
        (13, "performance"),
        (14, "quality"),
    ]

    def _set_widgets_from_rec(self, rec):
        """Seta cada widget diretamente pelo nome, sem depender de self.data + reset."""
        self.data["id"] = rec[0]
        for idx, name in self._FIELD_MAP:
            val = str(rec[idx]) if rec[idx] is not None else ""
            w = self.find_widget(name)
            if w is not None:
                w.value = val

    def _clear_widgets(self):
        """Limpa todos os widgets diretamente."""
        self.data["id"] = None
        for _, name in self._FIELD_MAP:
            w = self.find_widget(name)
            if w is not None:
                w.value = ""

    def _on_filter_select(self):
        """Carrega o registro selecionado no dropdown para os campos do formulario."""
        if getattr(self, "_resetting", False):
            return
        self._resetting = True
        selected_id = self._dropdown.value
        if selected_id is None:
            self._clear_widgets()
        else:
            rec = self.manager.get_by_id(selected_id)
            if rec:
                self._set_widgets_from_rec(rec)
        self._resetting = False
        self._update_oee()

    def reset(self):
        self._resetting = True
        # Atualizar opcoes do dropdown com registros atuais
        self._dropdown.options = self._get_machine_options()
        # Pre-selecionar o registro sendo editado no dropdown
        pending_id = getattr(self._list_frame, "_pending_edit_id", None)
        if pending_id is not None:
            self._dropdown.value = pending_id
            rec = self.manager.get_by_id(pending_id)
            if rec:
                # Popula data dict para que super().reset() tenha valores corretos
                self.data["id"] = rec[0]
                self.data["filter_machine"] = pending_id
                for idx, name in self._FIELD_MAP:
                    self.data[name] = str(rec[idx]) if rec[idx] is not None else ""
            super().reset()
            # Forcar widgets apos reset (garantia dupla)
            if rec:
                self._set_widgets_from_rec(rec)
        else:
            self.data["filter_machine"] = None
            self.data["id"] = None
            for _, name in self._FIELD_MAP:
                self.data[name] = ""
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
        self._resetting = True
        self._clear_widgets()
        self._dropdown.value = None
        self._resetting = False
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


class DashboardFrame(Frame):
    def __init__(self, screen, manager, data, list_frame):
        super().__init__(screen, screen.height, screen.width, data=data,
                         title="DASHBOARD OEE - PAINEL GERAL", can_scroll=False)
        self.manager = manager
        self._list_frame = list_frame

        self._dashboard_view = TextBox(Widget.FILL_FRAME, readonly=True, name="dashboard_view")

        layout = Layout([100], fill_frame=True)
        self.add_layout(layout)
        layout.add_widget(self._dashboard_view)

        buttons = Layout([1, 1])
        self.add_layout(buttons)
        buttons.add_widget(Button("Voltar", self._go_main), 0)
        buttons.add_widget(Button("Atualizar", self._refresh), 1)
        self.fix()

        self._update_dashboard()

    def _refresh(self):
        self._update_dashboard()

    def _go_main(self):
        raise NextScene("Main")

    def _update_dashboard(self):
        records = self.manager.get_all()

        SEP = "=" * 78
        THIN = "-" * 78

        lines = []
        lines.append(SEP)
        lines.append("              DASHBOARD OEE - PAINEL GERAL DE INDICADORES")
        lines.append(SEP)

        oee_global = availability_global = performance_global = quality_global = 0
        total_maquinas = 0
        disponibilidade_total = performance_total = qualidade_total = 0

        maquinas_data = []

        for rec in records:
            machine = str(rec[1])[:15]
            availability = float(rec[12] or 0)
            performance = float(rec[13] or 0)
            quality = float(rec[14] or 0)
            oee = calculate_oee(availability, performance, quality) * 100

            disponibilidade_total += availability
            performance_total += performance
            qualidade_total += quality
            total_maquinas += 1

            maquinas_data.append({
                'machine': machine,
                'availability': availability,
                'performance': performance,
                'quality': quality,
                'oee': oee
            })

        if total_maquinas > 0:
            availability_global = disponibilidade_total / total_maquinas
            performance_global = performance_total / total_maquinas
            quality_global = qualidade_total / total_maquinas
            oee_global = calculate_oee(availability_global, performance_global, quality_global) * 100

        lines.append("")
        lines.append(SEP)
        lines.append("                        INDICADORES GLOBAIS")
        lines.append(SEP)

        status_oee = calculate_status(oee_global / 100)
        if oee_global >= 85:
            emoji_status = "[★★★]"
        elif oee_global >= 75:
            emoji_status = "[★★ ]"
        elif oee_global >= 60:
            emoji_status = "[★  ]"
        else:
            emoji_status = "[   ]"

        lines.append(f"  OEE Global...: {oee_global:>6.2f}% {emoji_status}")
        lines.append(f"  Disponibilidade.: {availability_global:>6.2f}%")
        lines.append(f"  Performance....: {performance_global:>6.2f}%")
        lines.append(f"  Qualidade......: {quality_global:>6.2f}%")
        lines.append(f"  Maquinas.......: {total_maquinas:>6d}")
        lines.append(THIN)

        lines.append("")
        lines.append(SEP)
        lines.append("                     PERFORMANCE POR MAQUINA")
        lines.append(SEP)
        lines.append(f"  {'Maquina':<16} {'Disp':>7} {'Perf':>7} {'Qual':>7} {'OEE':>7} {'Status':<10}")
        lines.append(THIN)

        if maquinas_data:
            maquinas_data.sort(key=lambda x: x['oee'], reverse=True)
            for m in maquinas_data:
                status = calculate_status(m['oee'] / 100)
                if m['oee'] >= 85:
                    status_str = "EXCELLENT"
                elif m['oee'] >= 75:
                    status_str = "GOOD"
                elif m['oee'] >= 60:
                    status_str = "REGULAR"
                else:
                    status_str = "CRITICAL"

                lines.append(f"  {m['machine']:<16} {m['availability']:>6.1f}% {m['performance']:>6.1f}% {m['quality']:>6.1f}% {m['oee']:>6.1f}% {status_str:<10}")
        else:
            lines.append("  Nenhum dado cadastrado.")

        lines.append(THIN)
        lines.append("")
        lines.append(SEP)
        lines.append("                           METAS OEE")
        lines.append(SEP)
        lines.append(f"  Meta Global.......: 85.00%")
        linha_meta = ""
        if oee_global >= 85:
            linha_meta = "[ATINGIDA]"
        else:
            linha_meta = "[ABAIXO DA META]"
        lines.append(f"  Status Atual......: {oee_global:>6.2f}% {linha_meta}")
        lines.append(THIN)

        lines.append("")
        lines.append(SEP)
        lines.append("                     DISTRIBUICAO DE PERFORMANCE")
        lines.append(SEP)

        excelente = sum(1 for m in maquinas_data if m['oee'] >= 85)
        bom = sum(1 for m in maquinas_data if 75 <= m['oee'] < 85)
        regular = sum(1 for m in maquinas_data if 60 <= m['oee'] < 75)
        critico = sum(1 for m in maquinas_data if m['oee'] < 60)

        pct_exc = (excelente / total_maquinas * 100) if total_maquinas > 0 else 0
        pct_bom = (bom / total_maquinas * 100) if total_maquinas > 0 else 0
        pct_reg = (regular / total_maquinas * 100) if total_maquinas > 0 else 0
        pct_crit = (critico / total_maquinas * 100) if total_maquinas > 0 else 0

        linhas_grafico = [
            f"  Excelente (>=85%): {excelente:>3d} ({pct_exc:>5.1f}%) {'#' * excelente}" if excelente > 0 else f"  Excelente (>=85%): {excelente:>3d} ({pct_exc:>5.1f}%)",
            f"  Bom (75-85%)......: {bom:>3d} ({pct_bom:>5.1f}%) {'#' * bom}" if bom > 0 else f"  Bom (75-85%)......: {bom:>3d} ({pct_bom:>5.1f}%)",
            f"  Regular (60-75%).: {regular:>3d} ({pct_reg:>5.1f}%) {'#' * regular}" if regular > 0 else f"  Regular (60-75%).: {regular:>3d} ({pct_reg:>5.1f}%)",
            f"  Critico (<60%)...: {critico:>3d} ({pct_crit:>5.1f}%) {'!' * critico}" if critico > 0 else f"  Critico (<60%)...: {critico:>3d} ({pct_crit:>5.1f}%)",
        ]
        lines.extend(linhas_grafico)

        lines.append(THIN)
        lines.append("")
        lines.append(SEP)
        lines.append(f"  Atualizado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        lines.append(SEP)

        self._dashboard_view.value = lines
