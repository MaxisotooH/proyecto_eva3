from rest_framework import serializers

from .models import Producto

# Máximo de un INTEGER con signo: el mismo límite en MySQL y SQLite,
# así un número gigante da 400 en vez de un error de la base de datos.
MAXIMO_ENTERO = 2_147_483_647


class ProductoSerializer(serializers.ModelSerializer):
    """Convierte Producto <-> JSON y valida los datos recibidos."""

    categoria_nombre = serializers.CharField(source="get_categoria_display", read_only=True)

    class Meta:
        model = Producto
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
        read_only_fields = ["id", "fecha_creacion", "fecha_actualizacion"]
        extra_kwargs = {
            # Quitamos el validador automático de "unique" para usar el nuestro
            # (sin distinguir mayúsculas/minúsculas y con mensaje propio).
            "nombre": {"validators": []},
            "precio": {"min_value": 1, "max_value": MAXIMO_ENTERO},
            "stock": {"min_value": 0, "max_value": MAXIMO_ENTERO},
        }

    def validate_nombre(self, valor):
        """Requisito POST/PUT: el nombre del producto no debe existir en la BD."""
        valor = valor.strip()
        if not valor:
            raise serializers.ValidationError("El nombre no puede estar vacío.")

        repetidos = Producto.objects.filter(nombre__iexact=valor)
        if self.instance is not None:  # al actualizar, se excluye a sí mismo
            repetidos = repetidos.exclude(pk=self.instance.pk)
        if repetidos.exists():
            raise serializers.ValidationError(
                f"Ya existe un producto con el nombre '{valor}'."
            )
        return valor
