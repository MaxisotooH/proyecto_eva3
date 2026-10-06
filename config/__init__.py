"""
Paquete de configuración del proyecto.

Este archivo se ejecuta ANTES que todo lo demás (Django importa el paquete
"config" para leer settings.py), por eso es el lugar indicado para registrar
el conector de MySQL.

¿Por qué PyMySQL y no mysqlclient?
  - Django, para hablar con MySQL, busca un módulo llamado "MySQLdb"
    (el que instala el paquete mysqlclient).
  - mysqlclient está escrito en C y en algunos PC con Windows necesita
    compiladores para instalarse.
  - PyMySQL está escrito 100 % en Python: se instala con pip en cualquier PC.
  - install_as_MySQLdb() hace que PyMySQL se "presente" como MySQLdb,
    así Django lo usa sin notar la diferencia.
"""
import pymysql

pymysql.install_as_MySQLdb()
