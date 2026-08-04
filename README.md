# Bitácora FOTSI — Backend MySQL + Flask

Esta es la versión completa: base de datos real (MySQL) + servidor (backend en Python/Flask)
+ frontend. Las imágenes ahora se guardan como archivos reales en la carpeta `uploads/`,
y las operaciones viven en MySQL — ya no depende del navegador, así que no se va a borrar.

## Estructura del proyecto

```
BitacoraFOTSI/
├── server.py              <- backend (Flask)
├── requirements.txt       <- dependencias de Python
├── schema.sql             <- crea la base de datos y las tablas
├── import_backup.py       <- migra tu respaldo .json anterior (con imágenes)
├── static/
│   └── diario_magala.html <- frontend
└── uploads/                <- aquí se guardan las capturas de pantalla (se crea solo)
```

## Paso 1 — Instalar MySQL

Si no tienes MySQL instalado, la forma más fácil es instalar **XAMPP**:
https://www.apachefriends.org/es/download.html

1. Instala XAMPP.
2. Abre el "Panel de control de XAMPP".
3. Dale **Start** a "MySQL" (no necesitas iniciar Apache).

Si ya tienes MySQL instalado de otra forma, solo asegúrate de saber tu usuario/contraseña
(por defecto en XAMPP es usuario `root` sin contraseña, que es justo lo que ya está
configurado en `server.py`).

## Paso 2 — Crear la base de datos

Tienes dos formas, elige la que te sea más cómoda:

**Opción A — Con phpMyAdmin (viene incluido en XAMPP):**
1. Ve a http://localhost/phpmyadmin
2. Haz clic en la pestaña **"SQL"** arriba.
3. Abre el archivo `schema.sql` de este proyecto, copia todo su contenido, pégalo ahí.
4. Dale clic a **"Continuar"** / **"Go"**.

**Opción B — Desde la terminal:**
```
mysql -u root -p < schema.sql
```
(si tu contraseña está vacía, solo presiona Enter cuando te la pida)

## Paso 3 — Abrir el proyecto en Visual Studio Code

1. Abre VS Code.
2. Archivo → Abrir carpeta → selecciona la carpeta `BitacoraFOTSI`.
3. Abre una terminal integrada: menú **Terminal → Nueva terminal** (o Ctrl+ñ).

## Paso 4 — Instalar las dependencias de Python

En la terminal de VS Code (asegúrate de estar dentro de la carpeta `BitacoraFOTSI`):

```
pip install -r requirements.txt
```

Si `pip` no se reconoce, prueba con `pip3` o `python -m pip install -r requirements.txt`.

## Paso 5 — Ajustar la conexión (solo si es necesario)

Abre `server.py` en VS Code y revisa este bloque cerca del inicio:

```python
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "bitacora_fotsi",
}
```

Si tu MySQL tiene una contraseña distinta a vacía, o un usuario distinto a `root`,
cámbialo aquí.

## Paso 6 — Correr el servidor

En la terminal de VS Code:

```
python server.py
```

Deberías ver:
```
Bitácora FOTSI corriendo en http://localhost:5000
```

## Paso 7 — Abrir la bitácora

Ve a tu navegador y entra a:

```
http://localhost:5000
```

Guarda esta dirección en tus favoritos. **Mientras el servidor esté corriendo, tus datos
se guardan directo en MySQL** — no dependen del navegador, así que no importa si cierras
Chrome, reinicias la computadora, o limpias el caché: tus operaciones e imágenes van a
seguir ahí.

## (Opcional) Migrar tu respaldo anterior

Si tienes un archivo `.json` exportado de la versión anterior (con tus operaciones e
imágenes en base64), puedes migrarlo directo a la base de datos nueva:

```
python import_backup.py respaldo-bitacora-fotsi-2026-07-22.json
```

Esto va a:
- Insertar todas las operaciones en MySQL.
- Decodificar las imágenes que tenían en base64 y guardarlas como archivos reales dentro
  de `uploads/<id_operacion>/`.

## Cada vez que quieras usar la bitácora

1. Abre XAMPP y dale Start a MySQL (si no lo dejaste corriendo).
2. Abre la terminal en la carpeta del proyecto y corre `python server.py`.
3. Entra a `http://localhost:5000` desde tus favoritos.

## Notas importantes

- No borres la carpeta `uploads/` — ahí viven todas tus capturas de pantalla reales.
- Si quieres respaldar todo (por si formateas la compu), copia la carpeta `uploads/`
  completa y también exporta un respaldo `.json` desde el botón de la bitácora, o
  respalda la base de datos MySQL completa (`mysqldump bitacora_fotsi > respaldo.sql`).
- El capital inicial de referencia (para el % de rentabilidad) todavía se guarda en el
  navegador (localStorage), no en MySQL — es un dato menor, pero si cambias de
  computadora tendrás que volver a escribirlo una vez.
