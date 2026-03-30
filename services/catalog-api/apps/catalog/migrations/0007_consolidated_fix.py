from django.db import migrations, models

# ProductRecommendation, user_likes et user_recommendations sont déjà créés dans 0003 / 0005.
# Cette migration ne garde que les champs Order + renommage ProductRating (score → rating).


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0006_order_auto_shipped_at_productrating_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="phone",
            field=models.CharField(blank=True, max_length=20, default=""),
        ),
        migrations.AddField(
            model_name="order",
            name="email",
            field=models.EmailField(blank=True, max_length=254, default=""),
        ),
        migrations.AddField(
            model_name="order",
            name="city",
            field=models.CharField(blank=True, max_length=120, default=""),
        ),
        migrations.AddField(
            model_name="order",
            name="commune",
            field=models.CharField(blank=True, max_length=120, default=""),
        ),
        migrations.AddField(
            model_name="order",
            name="detailed_address",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="order",
            name="postal_code",
            field=models.CharField(blank=True, max_length=16, default=""),
        ),
        migrations.AddField(
            model_name="order",
            name="delivery_method",
            field=models.CharField(blank=True, max_length=20, default="domicile"),
        ),
        migrations.RenameField(
            model_name="productrating",
            old_name="score",
            new_name="rating",
        ),
        migrations.AddField(
            model_name="productrating",
            name="comment",
            field=models.TextField(blank=True, default=""),
        ),
    ]
