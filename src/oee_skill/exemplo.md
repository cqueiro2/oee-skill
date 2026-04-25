Atue como um Senior Python TUI Developer e UX Designer especializado em interfaces de terminal. 

Contexto: Estou construindo um projeto de OEE (Overall Equipment Effectiveness) e preciso da tela de "Relatório de Métricas". 

Tecnologias Obrigatórias: Python 3.10+, framework Textual e biblioteca Rich.

Seu objetivo é criar um código completo, executável e com um DESIGN EXCEPCIONAL. Não quero uma tela simples com tabelas sem graça. Quero um dashboard de terminal moderno, inspirado em interfaces de monitoramento industrial (SCADA/IIoT).

REQUISITOS DE DESIGN E LAYOUT:
1. Layout Estruturado: Use o sistema de Grid/Flexbox do Textual para criar um layout assimétrico e organizado (ex: um cabeçalho, uma área de "Hero" para o OEE geral, e colunas para as métricas secundárias).
2. O "Hero" (OEE Total): O valor principal do OEE (ex: 85.5%) deve ser o foco da tela. Use um `ProgressBar` grande e customizado, ou tipografia gigante com Rich, com cores dinâmicas baseadas no desempenho.
3. Lógica de Cores (World Class Standards):
   - Verde Vibrante (#00FF00 ou similar): OEE >= 85%
   - Amarelo/Alerta: OEE entre 60% e 84%
   - Vermelho/Danger: OEE < 60%
   Aplique essa regra de cores para o OEE geral e para os sub-indicadores.
4. Sub-métricas (Disponibilidade, Performance, Qualidade): Crie "cards" visuais para cada um. Inclua o percentual, uma barra de progresso menor e um pequeno texto de contexto (ex: "Tempo de parada: 45min").
5. Tabela de Perdas (The Big Six Losses): Use o Rich Table para mostrar as perdas categorizadas (Paradas Planejadas, Quebras, Setup, Pequenas Paradas, Velocidade Reduzida, Refugo). A tabela deve ter bordas elegantes e cores alternadas nas linhas (zebra stripe).
6. Rodapé/Footer: Adicione um rodapé com informações do sistema (ex: "Última atualização: HH:MM:SS", "Turno: A", "Linha de Produção: L1").

REQUISITOS TÉCNICOS:
- Use a separação de CSS do Textual (árquivo de CSS embutido via `CSS` string no Python) para estilizar o app, ao invés de focar apenas em estilos inline. Isso demonstra maturidade no uso do framework.
- Crie dados mock (fictícios, mas realistas) dentro do código para que a tela já abra populada.
- Use `reactive` variables do Textual para simular que os dados poderiam ser atualizados em tempo real.
- Oculte a barra de status padrão do Textual se ela poluir o design, ou customize-a para ficar transparente/limpa.
- Organize o código usando boas práticas (composição de widgets).
