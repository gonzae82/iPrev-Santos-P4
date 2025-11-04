-- init.sql

-- Cria o banco de dados principal, se ele não existir
CREATE DATABASE IF NOT EXISTS iprev_dados;

-- Seleciona o banco de dados para uso
USE iprev_dados;

-- Criação da Tabela 'despesas'
CREATE TABLE despesas (
    id INT AUTO_INCREMENT PRIMARY KEY, 
    ano SMALLINT NOT NULL,
    mes DATE NOT NULL, --  '2022-01-01'
    id_destino VARCHAR(20),
    id_centro_de_custos VARCHAR(20),
    id_natureza_despesa VARCHAR(20),
    area_de_atuacao VARCHAR(100),
    atribuicao VARCHAR(100), 
    contabilidade_do_gasto VARCHAR(50),
    favorecido VARCHAR(255),
    elementos_de_custo VARCHAR(255),
    conta_contabil VARCHAR(50),
    custo DECIMAL(12, 2) NOT NULL -- DECIMAL para valores monetários
);