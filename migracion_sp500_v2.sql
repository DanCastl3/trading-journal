-- Versión compatible con versiones más antiguas de MySQL (sin "IF NOT EXISTS")
-- Ejecuta esto en MySQL Workbench UNA SOLA VEZ.

USE bitacora_fotsi;

ALTER TABLE trades ADD COLUMN strategy VARCHAR(20) DEFAULT 'fotsi' AFTER id;
ALTER TABLE trades ADD COLUMN sma_trend_ok VARCHAR(5) AFTER strategy;
ALTER TABLE trades ADD COLUMN avg_pct_change VARCHAR(20) AFTER sma_trend_ok;
ALTER TABLE trades ADD COLUMN exit_reason VARCHAR(50) AFTER avg_pct_change;

-- Todas tus operaciones existentes de FOTSI ya quedan marcadas automáticamente como 'fotsi'
-- gracias al valor DEFAULT — no se pierde ni se altera ningún dato anterior.
