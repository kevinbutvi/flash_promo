from django.db import models
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.pk:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)


class Person(BaseModel):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    cuil = models.CharField(
        max_length=12,
        unique=True,
        validators=[
            RegexValidator(
                r"^\d{11}$", "El CUIL debe contener exactamente 11 dígitos numéricos."
            )
        ],
    )
    phone_number = models.CharField(
        max_length=15,
        validators=[
            RegexValidator(r"^\+?1?\d{9,15}$", "Ingrese un número telefónico válido.")
        ],
    )
    birth_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = "Persona"
        verbose_name_plural = "Personas"


# class Client(Person):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     address = models.CharField(max_length=255)
#     city = models.CharField(max_length=100)
#     province = models.CharField(max_length=100)
#     postal_code = models.CharField(max_length=10)

#     def __str__(self):
#         return f"{self.first_name} {self.last_name}"

#     class Meta:
#         verbose_name = "Cliente"
#         verbose_name_plural = "Clientes"
