# Generated by Django 5.1.6 on 2025-02-14 12:50

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Categories',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('image', models.JSONField(blank=True, null=True)),
                ('description', models.TextField()),
                ('display_order', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProductQuestions',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('question', models.TextField()),
                ('answer', models.TextField()),
                ('status', models.CharField(choices=[('ACTIVE', 'ACTIVE'), ('INACTIVE', 'INACTIVE')], default='ACTIVE', max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProductReviews',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('review_images', models.JSONField()),
                ('rating', models.FloatField()),
                ('reviews', models.TextField()),
                ('status', models.CharField(choices=[('ACTIVE', 'ACTIVE'), ('INACTIVE', 'INACTIVE')], default='ACTIVE', max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Products',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('image', models.JSONField()),
                ('description', models.TextField()),
                ('specifications', models.JSONField()),
                ('html_description', models.TextField()),
                ('highlights', models.JSONField()),
                ('sku', models.CharField(max_length=255)),
                ('initial_buying_price', models.FloatField()),
                ('initial_selling_price', models.FloatField()),
                ('weight', models.FloatField()),
                ('dimensions', models.CharField(default='0x0x0', max_length=255)),
                ('uom', models.CharField(max_length=255)),
                ('color', models.CharField(max_length=255)),
                ('tax_percentage', models.FloatField()),
                ('brand', models.CharField(max_length=255)),
                ('brand_model', models.CharField(max_length=255)),
                ('status', models.CharField(choices=[('ACTIVE', 'ACTIVE'), ('INACTIVE', 'INACTIVE')], default='ACTIVE', max_length=255)),
                ('seo_title', models.CharField(max_length=255)),
                ('seo_description', models.TextField()),
                ('seo_keywords', models.JSONField()),
                ('addition_details', models.JSONField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
