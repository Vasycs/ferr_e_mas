from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=10, decimal_places=0)
    descripcion = models.TextField()
    foto = models.ImageField(upload_to='productos/')

    def __str__(self):
        return self.nombre

class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.producto.nombre}"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    has_purchased = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

class ContactMessage(models.Model):
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField()
    mensaje = models.TextField()
    creado_el = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class Orden(models.Model):
    # Estados posibles de la orden
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente de Pago'),
        ('ESPERANDO_TRANSFERENCIA', 'Esperando Confirmación Bancaria'),
        ('PAGADA', 'Pagada Exitosamente'),
        ('RECHAZADA', 'Pago Rechazado'),
        ('CANCELADA', 'Cancelada por el Usuario / Timeout'),
    ]
    METODO_PAGO_CHOICES = [
        ('WEBPAY', 'Transbank Webpay Plus'),
        ('TRANSFERENCIA', 'Transferencia Bancaria'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    session_id = models.CharField(max_length=100, blank=True, null=True) # Para usuarios anónimos
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=30, choices=ESTADO_CHOICES, default='PENDIENTE')
    metodo_pago = models.CharField(max_length=20, choices=METODO_PAGO_CHOICES, default='WEBPAY')
    
    # Datos específicos para auditoría con Transbank
    total = models.PositiveIntegerField(help_text="Total pagado en CLP")
    token_ws = models.CharField(max_length=255, blank=True, null=True, help_text="Token de Webpay")
    codigo_autorizacion = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Orden {self.id} - {self.estado}"
    
class DetalleOrden(models.Model):
    orden = models.ForeignKey(Orden, related_name='detalles', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.PositiveIntegerField(help_text="Precio al momento de la compra")

    def subtotal(self):
        return self.cantidad * self.precio_unitario