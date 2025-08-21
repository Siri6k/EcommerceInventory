from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import ProductInteraction, Products

@receiver([post_save, post_delete], sender=ProductInteraction)
def update_product_counts(sender, instance, **kwargs):
    product = instance.product
    product.view_count = product.interactions.filter(action='view').count()
    product.like_count = product.interactions.filter(action='like').count()
    product.share_count = product.interactions.filter(action='share').count()
    product.save(update_fields=['view_count', 'like_count', 'share_count'])