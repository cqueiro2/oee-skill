# Sistema OEE (Overall Equipment Effectiveness)

Sistema para gerenciamento e monitoramento de métricas OEE de equipamentos industriais.

##Funcionalidades

- Cadastro de equipamentos com métricas OEE
- Cálculo automático de OEE (Disponibilidade x Performance x Qualidade)
- Cálculo de MTTR (Tempo Médio de Reparo)
- Cálculo de MTBF (Tempo Médio Entre Falhas)
- Registro de ocorrências e ações preventivas
- Acompanhamento de horas planejadas

##Campos do Cadastro

- Máquina
- Número do Equipamento
- Estação de Trabalho
- Data de Registro
- Data Prevista Liberação
- Tipo da Ocorrência
- Ação para Evitar
- Responsável
- Unidades Perdidas
- Produção Total
- Horas Plan
- Disponibilidade (%)
- Performance (%)
- Qualidade (%)

##Requisitos

- Python 3.8+
- asciimatics

##Instalação

```bash
pip install -r requirements.txt
```

##Execução

```bash
python src/oee_skill/main.py
```

##Uso

- **Novo**: Cadastrar novo equipamento
- **Editar**: Modificar equipamento selecionado
- **Excluir**: Remover equipamento
- **Sair**: Encerrar aplicação

##Tecnologias

- Python
- asciimatics (interface texto)
- SQLite (banco de dados)