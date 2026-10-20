BEGIN IMMEDIATE;

ALTER TABLE producao RENAME TO producao_legada;

CREATE TABLE producao (
    id INTEGER PRIMARY KEY,
    setor TEXT NOT NULL CHECK (length(trim(setor)) > 0),
    pecas_produzidas INTEGER NOT NULL DEFAULT 0 CHECK (pecas_produzidas >= 0),
    pecas_rejeitadas INTEGER NOT NULL DEFAULT 0
        CHECK (pecas_rejeitadas >= 0 AND pecas_rejeitadas <= pecas_produzidas),
    custo_unitario_centavos INTEGER NOT NULL CHECK (custo_unitario_centavos >= 0)
);

INSERT INTO producao (
    id, setor, pecas_produzidas, pecas_rejeitadas, custo_unitario_centavos
)
SELECT
    id, setor, pecas_produzidas, pecas_rejeitadas,
    CAST(ROUND(custo_unitario * 100) AS INTEGER)
FROM producao_legada;

DROP TABLE producao_legada;

COMMIT;