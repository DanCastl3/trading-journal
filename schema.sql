-- Esquema de base de datos para la Bitácora FOTSI (Magalà)
-- Ejecuta este archivo una sola vez para crear la base y las tablas.

CREATE DATABASE IF NOT EXISTS bitacora_fotsi
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE bitacora_fotsi;

-- Tabla principal de operaciones
CREATE TABLE IF NOT EXISTS trades (
  id VARCHAR(64) PRIMARY KEY,
  date DATE,
  pair VARCHAR(20),
  tf VARCHAR(10),
  broker VARCHAR(50) DEFAULT 'Saxo',
  time_entry VARCHAR(10),
  time_tp1 VARCHAR(10),
  time_tp2 VARCHAR(10),
  dir VARCHAR(10),
  div_fuerte VARCHAR(50),
  div_debil VARCHAR(50),
  atr VARCHAR(30),
  sl VARCHAR(30),
  entry_price VARCHAR(30),
  ema50 VARCHAR(30),
  ema100 VARCHAR(30),
  close1 VARCHAR(30),
  close2 VARCHAR(30),
  stop_adjust VARCHAR(50),
  capital VARCHAR(30),
  risk_pct VARCHAR(10) DEFAULT '2',
  status VARCHAR(20) DEFAULT 'open',
  tp1_desc TEXT,
  tp2_desc TEXT,
  pnl DECIMAL(14,2),
  breakeven VARCHAR(5) DEFAULT 'no',
  sesion VARCHAR(60),
  notes TEXT,
  created_at BIGINT,
  INDEX idx_date (date),
  INDEX idx_status (status)
) ENGINE=InnoDB;

-- Imágenes asociadas a cada operación (guardadas como archivos en disco, aquí solo la referencia)
CREATE TABLE IF NOT EXISTS trade_images (
  id INT AUTO_INCREMENT PRIMARY KEY,
  trade_id VARCHAR(64) NOT NULL,
  filename VARCHAR(255) NOT NULL,
  original_name VARCHAR(255),
  created_at BIGINT,
  FOREIGN KEY (trade_id) REFERENCES trades(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Configuración general (capital inicial de referencia, etc.)
CREATE TABLE IF NOT EXISTS settings (
  `key` VARCHAR(50) PRIMARY KEY,
  value TEXT
) ENGINE=InnoDB;

-- Plan de trading (los 5 pasos, guardados como filas clave/valor)
CREATE TABLE IF NOT EXISTS trading_plan (
  `key` VARCHAR(50) PRIMARY KEY,
  value TEXT
) ENGINE=InnoDB;
