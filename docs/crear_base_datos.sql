-- Ejecutar en MySQL Workbench o en la consola de MySQL antes de "migrate".
CREATE DATABASE IF NOT EXISTS tienda_api
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

-- (Opcional) usuario dedicado en vez de root.
-- Si lo usas, cambia DB_USER / DB_PASSWORD en config/settings.py.
-- CREATE USER IF NOT EXISTS 'tienda_user'@'localhost' IDENTIFIED BY 'tienda123';
-- GRANT ALL PRIVILEGES ON tienda_api.* TO 'tienda_user'@'localhost';
-- GRANT ALL PRIVILEGES ON test_tienda_api.* TO 'tienda_user'@'localhost';  -- para "manage.py test"
-- FLUSH PRIVILEGES;

-- Verificación después de migrar y cargar datos:
-- USE tienda_api;
-- SELECT * FROM productos;
