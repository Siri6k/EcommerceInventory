from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.hashers import make_password

import uuid


# Create your models here.
class Users(AbstractUser):
    anon_id = models.CharField(max_length=255, null=True, blank=True)
    username = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(unique=True)
    profile_pic = models.JSONField()
    password = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    whatsapp_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField()
    account_status = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        default="Active",
        choices=(
            ("Active", "Active"),
            ("Inactive", "Inactive"),
            ("Blocked", "Blocked"),
        ),
    )
    city = models.CharField(max_length=50, 
                            blank=True, 
                            null=True,
                            default="Kinshasa"
                            )
    province = models.CharField(max_length=50, blank=True, null=True,  default="Kinshasa")
    country = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        default="Congo",
        choices=(
            ("Congo", "Congo"),
            ("Tanzania", "Tanzania"),
            ("Angola", "Angola"),
            ("Zambia", "Zambia"),
            ("Burundi", "Burundi"),
            ("Uganda", "Uganda"),
            ("Zimbabwe", "Zimbabwe"),
            ("Others", "Others"),
            ("Congo-brazza", "Congo-brazza"),

        ),
    )
    role = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        default="Customer",
        choices=(
            ("Admin", "Admin"),
            ("Supplier", "Supplier"),
            ("Customer", "Customer"),
            ("Staff", "Staff"),
           
        ),
    )
    
    birthdate = models.DateField(blank=True, null=True)
    social_media_links = models.JSONField(blank=True, null=True)
    addition_details = models.JSONField(blank=True, null=True)
    language = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        default="French",
        choices=(
            ("English", "English"),
            ("French", "French"),
        ),
    )
    departMent = None
    designation = None
    time_zone = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        default="UTC+01:00",
        choices=(
            ("UTC-12:00", "UTC-12:00"),
            ("UTC-11:00", "UTC-11:00"),
            ("UTC-10:00", "UTC-10:00"),
            ("UTC-09:30", "UTC-09:30"),
            ("UTC-09:00", "UTC-09:00"),
            ("UTC-08:00", "UTC-08:00"),
            ("UTC-07:00", "UTC-07:00"),
            ("UTC-06:00", "UTC-06:00"),
            ("UTC-05:00", "UTC-05:00"),
            ("UTC-04:00", "UTC-04:00"),
            ("UTC-03:30", "UTC-03:30"),
            ("UTC-03:00", "UTC-03:00"),
            ("UTC-02:00", "UTC-02:00"),
            ("UTC-01:00", "UTC-01:00"),
            ("UTC", "UTC"),
            ("UTC+01:00", "UTC+01:00"),
            ("UTC+02:00", "UTC+02:00"),
            ("UTC+03:00", "UTC+03:00"),
            ("UTC+03:30", "UTC+03:30"),
            ("UTC+04:00", "UTC+04:00"),
            ("UTC+04:30", "UTC+04:30"),
            ("UTC+05:00", "UTC+05:00"),
            ("UTC+05:30", "UTC+05:30"),
            ("UTC+05:45", "UTC+05:45"),
            ("UTC+06:00", "UTC+06:00"),
            ("UTC+06:30", "UTC+06:30"),
            ("UTC+07:00", "UTC+07:00"),
            ("UTC+08:00", "UTC+08:00"),
            ("UTC+08:45", "UTC+08:45"),
            ("UTC+09:00", "UTC+09:00"),
            ("UTC+09:30", "UTC+09:30"),
            ("UTC+10:00", "UTC+10:00"),
            ("UTC+10:30", "UTC+10:30"),
            ("UTC+11:00", "UTC+11:00"),
            ("UTC+12:00", "UTC+12:00"),
            ("UTC+12:45", "UTC+12:45"),
            ("UTC+13:00", "UTC+13:00"),
            ("UTC+14:00", "UTC+14:00"),
        ),
    )
    last_login = models.DateTimeField(blank=True, null=True)
    last_device = models.CharField(blank=True, null=True, max_length=255)
    last_ip = models.GenericIPAddressField(blank=True, null=True)
    currency = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        default="CDF",
        choices=(
            ("CDF", "CDF"),
            ("USD", "USD"),
            ("EUR", "EUR"),
            ("GBP", "GBP"),
        ),
    )
    domain_user_id = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='domain_user_id_user'
    )

    domain_name = None
    plan_type = models.CharField(
        max_length=50,
        blank=True,
        default="Free",
        null=True,
        choices=(
            ("Free", "Free"),
            ("Basic", "Basic"),
            ("Standard", "Standard"),
            ("Premium", "Premium"),
            ("Enterprise", "Enterprise"),
        ),
    )
    added_by_user_id = models.ForeignKey(
        'self', on_delete=models.CASCADE, blank=True, null=True, related_name='added_by_user_id_user')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def defaultkey():
        return "username"

    def save(self, *args, **kwargs):
        # Synchroniser phone <-> whatsapp_number
        if self.phone_number and not self.whatsapp_number:
            self.whatsapp_number = self.phone_number
        elif self.whatsapp_number and not self.phone_number:
            self.phone_number = self.whatsapp_number

        is_new = self.pk is None
        super().save(*args, **kwargs)  # Sauvegarde initiale pour générer l'ID

        # Après création : si les champs ne sont pas définis
        if is_new and (not self.added_by_user_id or not self.domain_user_id):
            self.added_by_user_id = self
            
            super_admin = Users.objects.filter(role="Super Admin").first()
            self.domain_user_id = super_admin if super_admin else self

            super().save(update_fields=["added_by_user_id", "domain_user_id"])



class UserShippingAddress(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        Users, on_delete=models.CASCADE, related_name="user_shipping_address"
    )
    address_type = models.CharField(
        max_length=50,
        choices=(("Home", "Home"), ("Office", "Office"), ("Other", "Other")),
    )
    address = models.TextField()
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    pincode = models.CharField(max_length=10)
    country = models.CharField(
        max_length=50,
        choices=(
            ("Congo", "Congo"),
            ("Tanzania", "Tanzania"),
            ("Angola", "Angola"),
            ("Zambia", "Zambia"),
            ("Burundi", "Burundi"),
        ),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Modules(models.Model):
    id = models.AutoField(primary_key=True)
    module_name = models.CharField(max_length=50, unique=True)
    module_icon = models.CharField(null=True, blank=True, max_length=50)
    is_menu = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    module_url = models.CharField(null=True, blank=True, max_length=50)
    parent_id = models.ForeignKey(
        "self", on_delete=models.CASCADE, blank=True, null=True
    )
    display_order = models.IntegerField(default=0)
    module_description = models.CharField(
        null=True, blank=True, max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class UserPermissions(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        Users, on_delete=models.CASCADE, related_name="user_permissions_1"
    )
    module = models.ForeignKey(Modules, on_delete=models.CASCADE)
    is_permission = models.BooleanField(default=False)
    domain_user_id = models.ForeignKey(
        Users,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="domain_user_id_user_permissions",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ModuleUrls(models.Model):
    id = models.AutoField(primary_key=True)
    module = models.ForeignKey(
        Modules, on_delete=models.CASCADE, blank=True, null=True)
    url = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ActivityLog(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        Users, on_delete=models.CASCADE, related_name="user_activity_log"
    )
    activity = models.TextField()
    activity_type = models.CharField(max_length=50, blank=True)
    #activity_date = models.DateTimeField(auto_now_add=True)
    activity_ip = models.GenericIPAddressField()
    activity_device = models.CharField(blank=True, null=True, max_length=255)
    domain_user_id = models.ForeignKey(
        Users,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="domain_user_id_activity_log",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"[{self.activity_type}] - {self.user} - {self.activity}"

# all visitors 
class Visit(models.Model):
    ip_address = models.CharField(max_length=45)  # IPv6 support
    cookies = models.JSONField()  # Stockage JSON des cookies
    user_agent = models.TextField()
    anon_id = models.CharField(max_length=255, null=True, blank=True)
    visit_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"IP: {self.anon_id} - Date: {self.visit_date}"
