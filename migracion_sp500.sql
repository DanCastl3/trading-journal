-- Ejecuta esto en MySQL Workbench UNA SOLA VEZ para habilitar múltiples estrategias
-- en la misma bitácora (FOTSI y la nueva de SP500 Pullback).

USE bitacora_fotsi;

ALTER TABLE trades ADD COLUMN IF NOT EXISTS strategy VARCHAR(20) DEFAULT 'fotsi' AFTER id;
ALTER TABLE trades ADD COLUMN IF NOT EXISTS sma_trend_ok VARCHAR(5) AFTER strategy;
ALTER TABLE trades ADD COLUMN IF NOT EXISTS avg_pct_change VARCHAR(20) AFTER sma_trend_ok;
ALTER TABLE trades ADD COLUMN IF NOT EXISTS exit_reason VARCHAR(50) AFTER avg_pct_change;

-- Todas tus operaciones existentes de FOTSI ya quedan marcadas automáticamente como 'fotsi'
-- gracias al valor DEFAULT — no se pierde ni se altera ningún dato anterior.
