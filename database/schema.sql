CREATE TABLE IF NOT EXISTS producao (
    id INTEGER PRIMARY KEY,
    setor TEXT NOT NULL CHECK (length(trim(setor)) > 0),
    pecas_produzidas INTEGER NOT NULL DEFAULT 0 CHECK (pecas_produzidas >= 0),
    pecas_rejeitadas INTEGER NOT NULL DEFAULT 0
        CHECK (pecas_rejeitadas >= 0 AND pecas_rejeitadas <= pecas_produzidas),
    custo_unitario_centavos INTEGER NOT NULL CHECK (custo_unitario_centavos >= 0)
);