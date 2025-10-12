INSERT INTO despesas (
    mes, ano, servidor, cargo, descricao_funcao_gratificada, abrev, qtde, departamento, 
    vencimento, funcao_gratificada_2, gda, decimo_terceiro_sal, decimo_terceiro_sal_2, 
    ats, remuneracao_ferias, auxilio_alimentacao, faltas, soma_1, 
    patronal_capep, patronal_iprev, patronal_inss, patronal_cx_prev, soma_2, 
    custo_total, custo_hora, contrib_capep, contrib_iprev, contrib_inss, contrib_cx_previd
) VALUES 
(
    9, 2025, 'JOÃO DA SILVA', 'ANALISTA DE PREVIDÊNCIA', 'CHEFE DE SEÇÃO', 'ANS', 1, 'DEPARTAMENTO FINANCEIRO',
    5500.00, 1200.00, 300.00, 0.00, 0.00, 
    150.00, 0.00, 850.00, 0.00, 8000.00,  -- soma_1 = 5500+1200+300+150+850
    0.00, 880.00, 0.00, 0.00, 880.00,    -- soma_2 = 880
    8880.00, 40.36, 0.00, 770.00, 0.00, 0.00 -- custo_total = soma_1 + soma_2; custo_hora ~ custo_total / 220
),
(
    9, 2025, 'MARIA SOUZA', 'TÉCNICO ADMINISTRATIVO', NULL, 'TEC', 1, 'RECURSOS HUMANOS',
    3800.00, 0.00, 0.00, 0.00, 0.00, 
    80.00, 0.00, 850.00, 0.00, 4730.00,   -- soma_1 = 3800+80+850
    0.00, 520.30, 0.00, 0.00, 520.30,    -- soma_2 = 520.30
    5250.30, 23.86, 0.00, 418.00, 0.00, 0.00 -- custo_total = soma_1 + soma_2; custo_hora ~ custo_total / 220
);
