import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Producto",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nombre", models.CharField(max_length=100, unique=True, verbose_name="nombre")),
                ("descripcion", models.TextField(blank=True, default="", verbose_name="descripción")),
                ("precio", models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1)], verbose_name="precio")),
                ("stock", models.PositiveIntegerField(default=0, verbose_name="stock")),
                ("categoria", models.CharField(
                    choices=[
                        ("ELECTRONICA", "Electrónica"),
                        ("HOGAR", "Hogar"),
                        ("ALIMENTOS", "Alimentos"),
                        ("ROPA", "Ropa"),
                        ("DEPORTES", "Deportes"),
                        ("OTROS", "Otros"),
                    ],
                    default="OTROS",
                    max_length=20,
                    verbose_name="categoría",
                )),
                ("activo", models.BooleanField(default=True, verbose_name="activo")),
                ("fecha_creacion", models.DateTimeField(auto_now_add=True, verbose_name="fecha de creación")),
                ("fecha_actualizacion", models.DateTimeField(auto_now=True, verbose_name="última actualización")),
            ],
            options={
                "verbose_name": "producto",
                "verbose_name_plural": "productos",
                "db_table": "productos",
                "ordering": ["id"],
            },
        ),
    ]
