"""
Serializers de la app "productos".

Un SERIALIZER es el "traductor" entre el modelo y el JSON:
  - Serializar:    objeto Producto  -> diccionario -> JSON   (respuestas GET)
  - Deserializar:  JSON -> diccionario validado -> Producto  (POST / PUT)
Además VALIDA los datos recibidos: tipos, largos, mínimos, nombre único, etc.
Si algo no es válido, DRF responde 400 con el detalle de cada campo.
"""
from rest_framework import serializers

from .models import Producto

# Máximo de un INTEGER con signo (2^31 - 1). Es un límite seguro tanto en
# MySQL como en SQLite: así un número gigante responde 400 (dato inválido)
# en lugar de provocar un error de la base de datos.
MAXIMO_ENTERO = 2_147_483_647


class ProductoSerializer(serializers.ModelSerializer):
    """Convierte Producto <-> JSON y valida los datos recibidos."""

    # Campo extra, solo de lectura: la etiqueta legible de la categoría
    # ("Electrónica" en vez de "ELECTRONICA"). source= indica de dónde sale:
    # get_categoria_display() es un método que Django crea por usar choices.
    categoria_nombre = serializers.CharField(source="get_categoria_display", read_only=True)

    class Meta:
        model = Producto
        # Campos que aparecen en el JSON (y en este orden).
        fields = [
            "id",
            "nombre",
            "descripcion",
            "precio",
            "stock",
            "categoria",
            "categoria_nombre",
            "activo",
            "fecha_creacion",
            "fecha_actualizacion",
        ]
        # Campos que el cliente NO puede enviar ni modificar: los pone el sistema.
        read_only_fields = ["id", "fecha_creacion", "fecha_actualizacion"]
        extra_kwargs = {
            # Se quita el validador automático de "unique" que DRF crea a partir
            # del modelo, para usar el nuestro (validate_nombre): no distingue
            # mayúsculas/minúsculas e ignora espacios, con un mensaje propio.
            "nombre": {"validators": []},
            # Rango permitido de los números (si no se cumple -> 400).
            "precio": {"min_value": 1, "max_value": MAXIMO_ENTERO},
            "stock": {"min_value": 0, "max_value": MAXIMO_ENTERO},
        }

    def validate_nombre(self, valor):
        """
        Requisito del enunciado (POST): el nombre del producto no debe existir en la BD.

        DRF llama automáticamente a los métodos validate_<campo>() durante
        is_valid(). Lo que se retorna es el valor que finalmente se guarda.
        """
        # Se quitan los espacios del inicio y del final: "  Café " == "Café".
        valor = valor.strip()
        if not valor:
            raise serializers.ValidationError("El nombre no puede estar vacío.")

        # nombre__iexact: comparación SIN distinguir mayúsculas ("café" == "CAFÉ").
        repetidos = Producto.objects.filter(nombre__iexact=valor)
        # Al ACTUALIZAR (self.instance existe) el producto se excluye a sí mismo;
        # si no, no se podría guardar un PUT que mantiene el mismo nombre.
        if self.instance is not None:
            repetidos = repetidos.exclude(pk=self.instance.pk)
        if repetidos.exists():
            raise serializers.ValidationError(
                f"Ya existe un producto con el nombre '{valor}'."
            )
        return valor
