from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0007_consolidated_fix"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="brand",
            field=models.CharField(blank=True, max_length=120),
        ),
        migrations.AddField(
            model_name="product",
            name="is_featured",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="product",
            name="low_stock_threshold",
            field=models.PositiveIntegerField(default=12),
        ),
        migrations.AddField(
            model_name="product",
            name="min_order_quantity",
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AddField(
            model_name="product",
            name="unit_label",
            field=models.CharField(blank=True, max_length=80),
        ),
    ]
