"""
Modelos de la app "productos".

Un MODELO es una clase de Python que representa una TABLA de la base de datos:
cada atributo es una columna y cada objeto (instancia) es una fila.
Django genera el SQL por nosotros con "makemigrations" + "migrate".
"""
from django.core.validators import MinValueValidator
from django.db import models


class Producto(models.Model):
    """Producto que se expone en la API REST y se guarda en MySQL (tabla "productos")."""

    class Categoria(models.TextChoices):
        """
        Lista cerrada de categorías permitidas.

        Cada opción tiene dos partes: el VALOR que se guarda en la base de
        datos ("ELECTRONICA") y la ETIQUETA legible que se muestra ("Electrónica").
        """
        ELECTRONICA = "ELECTRONICA", "Electrónica"
        HOGAR = "HOGAR", "Hogar"
        ALIMENTOS = "ALIMENTOS", "Alimentos"
        ROPA = "ROPA", "Ropa"
        DEPORTES = "DEPORTES", "Deportes"
        OTROS = "OTROS", "Otros"

    # La columna "id" (clave primaria autoincremental) la crea Django solo.

    # unique=True: MySQL no permite dos productos con el mismo nombre.
    # (El serializer además lo valida antes, para responder un 400 claro.)
    nombre = models.CharField("nombre", max_length=100, unique=True)
    # blank=True: el campo puede venir vacío; default="": valor si no se envía.
    descripcion = models.TextField("descripción", blank=True, default="")
    # Pesos chilenos: número entero, sin decimales, y como mínimo $1.
    precio = models.PositiveIntegerField("precio", validators=[MinValueValidator(1)])
    stock = models.PositiveIntegerField("stock", default=0)
    # choices=...: solo acepta los valores definidos en la clase Categoria.
    categoria = models.CharField(
        "categoría",
        max_length=20,
        choices=Categoria.choices,
        default=Categoria.OTROS,
    )
    activo = models.BooleanField("activo", default=True)
    # auto_now_add: se llena una sola vez, al crear el registro.
    fecha_creacion = models.DateTimeField("fecha de creación", auto_now_add=True)
    # auto_now: se actualiza sola cada vez que se guarda el registro.
    fecha_actualizacion = models.DateTimeField("última actualización", auto_now=True)

    class Meta:
        db_table = "productos"          # nombre real de la tabla en MySQL
        ordering = ["id"]               # orden por defecto en las consultas
        verbose_name = "producto"       # nombres que se ven en el admin
        verbose_name_plural = "productos"

    def __str__(self):
        """Texto con que se muestra el producto (admin, consola, etc.)."""
        return f"{self.nombre} (${self.precio})"
