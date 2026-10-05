from django.core.validators import MinValueValidator
from django.db import models


class Producto(models.Model):
    """Producto que se expone en la API REST y se guarda en MySQL."""

    class Categoria(models.TextChoices):
        ELECTRONICA = "ELECTRONICA", "Electrónica"
        HOGAR = "HOGAR", "Hogar"
        ALIMENTOS = "ALIMENTOS", "Alimentos"
        ROPA = "ROPA", "Ropa"
        DEPORTES = "DEPORTES", "Deportes"
        OTROS = "OTROS", "Otros"

    nombre = models.CharField("nombre", max_length=100, unique=True)
    descripcion = models.TextField("descripción", blank=True, default="")
    # Pesos chilenos: entero, sin decimales
    precio = models.PositiveIntegerField("precio", validators=[MinValueValidator(1)])
    stock = models.PositiveIntegerField("stock", default=0)
    categoria = models.CharField(
        "categoría",
        max_length=20,
        choices=Categoria.choices,
        default=Categoria.OTROS,
    )
    activo = models.BooleanField("activo", default=True)
    fecha_creacion = models.DateTimeField("fecha de creación", auto_now_add=True)
    fecha_actualizacion = models.DateTimeField("última actualización", auto_now=True)

    class Meta:
        db_table = "productos"
        ordering = ["id"]
        verbose_name = "producto"
        verbose_name_plural = "productos"

    def __str__(self):
        return f"{self.nombre} (${self.precio})"
