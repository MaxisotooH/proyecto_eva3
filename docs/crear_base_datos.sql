-- ============================================================================
-- crear_base_datos.sql
-- Crea la base de datos del proyecto en MySQL / MariaDB.
--
-- Es la alternativa MANUAL al comando:   python manage.py crear_base_datos
-- (ambos hacen lo mismo; basta con usar uno de los dos).
--
-- Dónde ejecutarlo: MySQL Workbench, phpMyAdmin (pestaña SQL) o la consola:
--     mysql -u root -p < docs/crear_base_datos.sql
-- Después: python manage.py migrate   (crea las TABLAS dentro de la base)
-- ============================================================================

-- 1) Base de datos. utf8mb4 guarda tildes, ñ y emojis; utf8mb4_unicode_ci
--    compara textos sin distinguir mayúsculas ("café" = "CAFÉ").
CREATE DATABASE IF NOT EXISTS tienda_api
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

-- 2) (Opcional) Usuario exclusivo del proyecto, en vez de usar root.
--    Si lo usas, define DB_USER=tienda_user y DB_PASSWORD=tienda123
--    (ver DOCUMENTACION.md, sección "Variables de entorno").
-- CREATE USER IF NOT EXISTS 'tienda_user'@'localhost' IDENTIFIED BY 'tienda123';
-- GRANT ALL PRIVILEGES ON tienda_api.* TO 'tienda_user'@'localhost';
-- Permiso para la base temporal que crea "python manage.py test":
-- GRANT ALL PRIVILEGES ON test_tienda_api.* TO 'tienda_user'@'localhost';
-- FLUSH PRIVILEGES;

-- 3) Verificación después de migrar y cargar los datos de ejemplo:
-- USE tienda_api;
-- SELECT * FROM productos;
