-- Ejecuta esto en MySQL Workbench UNA SOLA VEZ si ya habías creado la base de datos
-- antes de este cambio (agrega el campo para el stop ajustado tras TP1).

USE bitacora_fotsi;

ALTER TABLE trades ADD COLUMN IF NOT EXISTS stop_adjust VARCHAR(50) AFTER close2;
