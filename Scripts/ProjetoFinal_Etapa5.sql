
-- ===============================
-- VIEW
-- ===============================
-- View para listar jogos e suas plataformas
CREATE OR REPLACE VIEW VW_DETALHES_JOGOS AS
SELECT 
    J.TITULO AS JOGO,
    J.GENERO,
    P.NOME AS PLATAFORMA,
    J.ANO_LANCAMENTO,
    J.HORAS_JOGADAS
FROM JOGO J
JOIN PLATAFORMA P ON J.ID_PLATAFORMA = P.ID_PLATAFORMA;

-- Exemplo de uso:
-- SELECT * FROM VW_DETALHES_JOGOS WHERE GENERO = 'RPG';

-- ===============================
-- VIEW MATERIALIZADA
-- ===============================

-- View Materializada para estatísticas de biblioteca por usuário
CREATE MATERIALIZED VIEW MV_ESTATISTICAS_USUARIO AS
SELECT 
    U.NOME AS USUARIO,
    COUNT(UJ.ID_JOGO) AS TOTAL_JOGOS,
    ROUND(AVG(UJ.AVALIACAO), 2) AS MEDIA_AVALIACOES,
    SUM(J.HORAS_JOGADAS) AS TOTAL_HORAS_ACUMULADAS
FROM USUARIO U
LEFT JOIN USUARIO_JOGO UJ ON U.ID_USUARIO = UJ.ID_USUARIO
LEFT JOIN JOGO J ON UJ.ID_JOGO = J.ID_JOGO
GROUP BY U.ID_USUARIO, U.NOME;

-- Para atualizar os dados:
-- REFRESH MATERIALIZED VIEW MV_ESTATISTICAS_USUARIO;

-- ===============================
-- TRIGGERS
-- ===============================

-- Valida se a DATA_FIM não é anterior à DATA_INICIO antes de inserir ou atualizar um registro de jogo do usuário.
CREATE OR REPLACE FUNCTION FN_VALIDA_DATAS_JOGO()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.DATA_FIM IS NOT NULL AND NEW.DATA_FIM < NEW.DATA_INICIO THEN
        RAISE EXCEPTION 'A data de término não pode ser anterior à data de início.';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER TRG_VALIDA_DATAS_USUARIO_JOGO
BEFORE INSERT OR UPDATE ON USUARIO_JOGO
FOR EACH ROW EXECUTE FUNCTION FN_VALIDA_DATAS_JOGO();


--Sempre que um jogo for concluído (Status = 3), a trigger registra automaticamente a data atual no campo DATA_FIM, caso ele esteja nulo.
CREATE OR REPLACE FUNCTION FN_LOG_CONCLUSAO_JOGO()
RETURNS TRIGGER AS $$
BEGIN
    -- Se o status mudou para 3 (Concluído) e a data fim está vazia
    IF NEW.STATUS = 3 AND NEW.DATA_FIM IS NULL THEN
        UPDATE USUARIO_JOGO 
        SET DATA_FIM = CURRENT_DATE 
        WHERE ID_USUARIO = NEW.ID_USUARIO AND ID_JOGO = NEW.ID_JOGO;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER TRG_CONCLUI_JOGO
AFTER UPDATE OF STATUS ON USUARIO_JOGO
FOR EACH ROW EXECUTE FUNCTION FN_LOG_CONCLUSAO_JOGO();


-- ===============================
-- PROCEDURE
-- ===============================

-- Procedure para adicionar horas jogadas a um jogo
CREATE OR REPLACE PROCEDURE PR_ADICIONAR_HORAS_JOGO(
    p_id_jogo INT,
    p_horas_adicionais DECIMAL
)
LANGUAGE plpgsql
AS $$
BEGIN
    IF p_horas_adicionais < 0 THEN
        RAISE NOTICE 'Não é possível adicionar horas negativas.';
    ELSE
        UPDATE JOGO 
        SET HORAS_JOGADAS = HORAS_JOGADAS + p_horas_adicionais
        WHERE ID_JOGO = p_id_jogo;
        
        RAISE NOTICE 'Horas atualizadas com sucesso para o jogo ID %', p_id_jogo;
    END IF;
END;
$$;

-- Exemplo de execução:
-- CALL PR_ADICIONAR_HORAS_JOGO(1, 10.5);	

