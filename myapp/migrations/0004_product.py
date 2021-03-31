# Generated by Django 3.0 on 2021-03-12 04:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0003_user_usertype'),
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_category', models.CharField(choices=[('chair', 'chair'), ('sofa', 'sofa'), ('lamp', 'lamp'), ('table', 'table')], max_length=100)),
                ('product_name', models.CharField(max_length=100)),
                ('product_price', models.CharField(max_length=100)),
                ('product_desc', models.TextField()),
                ('product_image', models.ImageField(upload_to='images/')),
            ],
        ),
    ]