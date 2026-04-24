# Exemplo de uso da tela de gráficos do OEE
# Cada métrica deve ser informada em porcentagem (0‑100)

metricas = ['Disponibilidade', 'Performance', 'Qualidade', 'Eficiência']

# Valores de exemplo (em %) — substitua pelos valores reais da sua base de dados
valores = [85, 90, 78, 70]  # Disponibilidade, Performance, Qualidade, Eficiência

def draw_bar_graph(value: float, label: str = "", width: int = 30) -> str:
    """Desenha um gráfico de barra ASCII similar ao da aplicação.
    """
    max_val = 100.0
    percent = min(max(value, 0), max_val)
    filled = int((percent / max_val) * width)
    bar = "█" * filled + "░" * (width - filled)
    return f"{label:<15} [{bar}] {percent:>5.1f}%"

print('\nGráfico de Métricas OEE:')
print(f"{'Métrica':>15} {'Valor':>8}   Gráfico")

for nome, valor in zip(metricas, valores):
    print(draw_bar_graph(valor, nome))