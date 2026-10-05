# PyMySQL actúa como conector MySQL para Django (reemplazo de mysqlclient).
# Es Python puro, así que se instala sin compiladores en Windows.
import pymysql

pymysql.install_as_MySQLdb()
