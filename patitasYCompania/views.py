from decimal import Decimal, ROUND_DOWN, ROUND_HALF_UP
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.core.mail import send_mail
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, User
from transbank.webpay.webpay_plus.transaction import Transaction
from transbank.error.transbank_error import TransbankError
from transbank.common.options import WebpayOptions
from transbank.common.integration_commerce_codes import IntegrationCommerceCodes
from transbank.common.integration_api_keys import IntegrationApiKeys
from transbank.common.integration_type import IntegrationType
import uuid

from Prueba.settings import EMAIL_HOST_USER
from .models import Producto, Profile, CartItem
from .forms import ContactForm, LoginForm, ProductoForm, RegistroUsuarioForm
import json
from django.core.mail import EmailMessage 
from django.core.mail import send_mail

# Configuramos las credenciales públicas de prueba (Integration)
opciones_webpay = WebpayOptions(
    IntegrationCommerceCodes.WEBPAY_PLUS,
    IntegrationApiKeys.WEBPAY,
    IntegrationType.TEST
)

# Vistas de la Página Principal
def index(request):
    productos_populares = Producto.objects.all()[:3]
    return render(request, 'patitasYCompania/index.html', {'productos_populares': productos_populares})

def success(request):
    return render(request, 'patitasYCompania/success.html')

def success_compra(request):
    return render(request, 'patitasYCompania/success_compra.html')

# Vistas de Autenticación
def registro(request):
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            
            cliente_group, created = Group.objects.get_or_create(name='Cliente')
            user.groups.add(cliente_group)

            body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
                <div style="max-width: 600px; margin: auto; background-color: #ffffff; padding: 20px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);">
                    <h2 style="color: #333;">¡Bienvenido a Patitas y Compañía, {user.username}!</h2>
                    <p style="color: #555;">Gracias por registrarte en nuestra tienda. Nos alegra que formes parte de nuestra comunidad de amantes de las mascotas.</p>
                    <p style="color: #555;">Como agradecimiento, te ofrecemos un <strong>30% de descuento</strong> en tu primera compra. ¡No te lo pierdas!</p>
                    <p style="color: #555;">Si tienes alguna pregunta, no dudes en contactarnos. ¡Estamos aquí para ayudarte!</p>
                    <p style="color: #777; font-size: 0.9em;">&copy; 2024 Patitas y Compañía</p>
                </div>
            </body>
            </html>
            """

            email = EmailMessage(
                'Registro Exitoso en Patitas y Compañía',
                body,
                EMAIL_HOST_USER,
                [user.email]
            )
            email.content_subtype = 'html'
            email.send(fail_silently=False)
            
            auth_login(request, user)
            messages.success(request, "Registro exitoso. Bienvenido a Patitas y Compañía.")
            return redirect('user_profile')
    else:
        form = RegistroUsuarioForm()
    return render(request, 'patitasYCompania/registro.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)
                return redirect('index')
            else:
                return render(request, 'patitasYCompania/login.html', {'form': form, 'error': 'Credenciales incorrectas'})
    else:
        form = LoginForm()
    return render(request, 'patitasYCompania/login.html', {'form': form})

@login_required
def user_logout(request):
    auth_logout(request)
    return redirect('index')

@login_required
def user_profile(request):
    user = request.user
    if request.method == 'POST':
        user.first_name = request.POST.get('nombre')
        user.profile.telefono = request.POST.get('telefono')
        user.profile.direccion = request.POST.get('direccion')
        user.save()
        user.profile.save()
        messages.success(request, 'Perfil actualizado correctamente.')
        return redirect('user_profile')
    return render(request, 'patitasYCompania/perfil.html', {'usuario': user})

@login_required
def delete_user(request):
    if request.method == 'POST':
        user = request.user
        user.delete()
        messages.success(request, "Tu cuenta ha sido eliminada exitosamente.")
        return redirect('index')

# Vistas de Producto
def product_list(request):
    products = Producto.objects.all()
    return render(request, 'patitasYCompania/productos.html', {'products': products})
 
def product_detail(request, product_id):
    product = get_object_or_404(Producto, id=product_id)
    return render(request, 'patitasYCompania/producto.html', {'product': product})

@login_required
def product_create(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductoForm()
    return render(request, 'patitasYCompania/product_form.html', {'form': form})

@login_required
def product_update(request, product_id):
    product = get_object_or_404(Producto, id=product_id)
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_detail', product_id=product.id)
    else:
        form = ProductoForm(instance=product)
    return render(request, 'patitasYCompania/product_form.html', {'form': form})

@login_required
def product_delete(request, product_id):
    product = get_object_or_404(Producto, id=product_id)
    if request.method == 'POST':
        product.delete()
        return redirect('product_list')
    return render(request, 'patitasYCompania/product_confirm_delete.html', {'product': product})

# Vistas de Contacto
def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            enviar_correo_contacto(form.cleaned_data)
            return redirect('success')
    else:
        form = ContactForm()
    return render(request, 'patitasYCompania/contacto.html', {'form': form})

# Vistas de Carrito de Compras
@login_required
def add_to_cart(request, product_id):
    producto = get_object_or_404(Producto, id=product_id)
    cart_item, created = CartItem.objects.get_or_create(user=request.user, producto=producto)
    if not created:
        cart_item.quantity += 1
    cart_item.save()
    messages.success(request, f'¡{producto.nombre} ha sido añadido al carrito!')
    return redirect('cart')



@login_required
def cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    subtotal = sum(Decimal(item.producto.precio) * item.quantity for item in cart_items)
    iva = subtotal * Decimal('0.19')
    total_iva = subtotal

    if not request.user.profile.has_purchased:
        descuento = total_iva * Decimal('0.30')
        total_con_descuento = total_iva - descuento
    else:
        descuento = Decimal('0')
        total_con_descuento = total_iva

    subtotal = str(int(subtotal))
    iva = str(int(iva))
    total_iva = str(int(total_iva))
    total_con_descuento = str(int(total_con_descuento))
    descuento = str(int(descuento))

    return render(request, 'patitasYCompania/cart.html', {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'total_iva': total_iva,
        'iva': iva,
        'descuento': descuento,
        'total_con_descuento': total_con_descuento,
    })


@login_required
def update_cart(request, item_id, action):
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    if action == 'increment':
        cart_item.quantity += 1
    elif action == 'decrement' and cart_item.quantity > 1:
        cart_item.quantity -= 1
    cart_item.save()
    return JsonResponse({'message': 'Carrito actualizado correctamente'})

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    cart_item.delete()
    messages.success(request, 'El producto ha sido eliminado del carrito.')
    return redirect('cart')

@login_required
def clear_cart(request):
    CartItem.objects.filter(user=request.user).delete()
    messages.success(request, 'El carrito ha sido vaciado.')
    return redirect('cart')

@login_required
def checkout(request):
    cart_items = CartItem.objects.filter(user=request.user)
    subtotal = sum(Decimal(item.producto.precio) * item.quantity for item in cart_items)
    iva = subtotal * Decimal('0.19')
    total_iva = subtotal

    if not request.user.profile.has_purchased:
        descuento = total_iva * Decimal('0.30')
        total_con_descuento = total_iva - descuento
    else:
        descuento = Decimal('0')
        total_con_descuento = total_iva

    subtotal = str(int(subtotal))
    iva = str(int(iva))
    total_iva = str(int(total_iva))
    total_con_descuento = str(int(total_con_descuento))
    descuento = str(int(descuento))

    # 1. Preparar los datos (Aquí conectas con tu Carrito de compras)
    monto_total = total_con_descuento # Reemplazar con la suma del carrito
    orden_compra = str(uuid.uuid4())[:26] # Generar ID único para la orden
    id_sesion = request.session.session_key or "sesion_anonima"
    
    # URL absoluta a la que Transbank enviará al usuario de vuelta
    url_retorno = request.build_absolute_uri(reverse('webpay_commit'))

    try:
        tx = Transaction(opciones_webpay)
        # 2. Crear la transacción en el entorno de Integración
        respuesta = tx.create(
            buy_order=orden_compra,
            session_id=id_sesion,
            amount=total_con_descuento,
            return_url=url_retorno
        )
        
        # 3. Pasar los datos al template que hará la redirección
        contexto = {
            "url_transbank": respuesta['url'],
            "token": respuesta['token']
        }
        # IMPORTANTE: Aquí deberías crear la orden en MySQL con estado "Pendiente"
        
        return render(request, 'patitasYCompania/pago_redirect.html', contexto)

    except TransbankError as e:
        # Manejo de excepciones si la API de Transbank no responde
        return render(request, 'patitasYCompania/error.html', {"error": str(e)})


def webpay_commit(request):
    # 1. Capturar el token. Webpay lo envía por GET en éxito, o POST si el usuario aborta.
    token = request.GET.get('token_ws') or request.POST.get('token_ws')

    if not token:
        # Si no hay token, el usuario cerró la ventana de pago o anuló
        # Aquí buscarías la orden Pendiente en la base de datos y la marcarías como "Cancelada"
        return render(request, 'patitasYCompania/pago_cancelado.html')

    try:
        tx = Transaction(opciones_webpay)
        # 2. Confirmar el pago criptográficamente
        respuesta = tx.commit(token)

        # 3. Validar el estado
        if respuesta['status'] == 'AUTHORIZED':
            # ¡Pago exitoso!
            # Lógica de datos: Marcar orden como "Pagada", descontar stock, vaciar carrito.
            return render(request, 'patitasYCompania/exito.html', {"detalle": respuesta})
        else:
            # Transacción rechazada (ej. sin fondos, tarjeta bloqueada)
            return render(request, 'patitasYCompania/rechazado.html', {"detalle": respuesta})

    except TransbankError as e:
        # Esto ocurre si el token ya fue usado (doble confirmación) o es inválido
        return render(request, 'patitasYCompania/error.html', {"error": str(e)})

   



# Vistas de Prueba de Envío de Correo
def test_email(request):
    try:
        send_mail(
            'Prueba de Envío de Correo',
            'Este es un correo de prueba.',
            EMAIL_HOST_USER,
            ['destinatario@example.com'],
            fail_silently=False,
        )
        return HttpResponse("Correo enviado correctamente")
    except Exception as e:
        return HttpResponse(f"Error al enviar el correo: {e}")

# Funciones Auxiliares
def enviar_correo_contacto(data):
    try:
        subject = 'Nuevo mensaje de contacto'
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
            <div style="max-width: 600px; margin: auto; background-color: #ffffff; padding: 20px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);">
                <h2 style="color: #333;">Nuevo Mensaje de Contacto</h2>
                <p style="color: #555;">Has recibido un nuevo mensaje de contacto en Patitas y Compañía.</p>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd;">Nombre:</td>
                        <td style="padding: 8px; border: 1px solid #ddd;">{data.get("nombre")}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd;">Teléfono:</td>
                        <td style="padding: 8px; border: 1px solid #ddd;">{data.get("telefono")}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd;">Correo Electrónico:</td>
                        <td style="padding: 8px; border: 1px solid #ddd;">{data.get("email")}</td>
                    </tr>
                </table>
                <p style="color: #555; margin-top: 20px;">Gracias por usar nuestro servicio.</p>
                <p style="color: #777; font-size: 0.9em;">&copy; 2024 Patitas y Compañía</p>
            </div>
        </body>
        </html>
        """
        
        email = EmailMessage(
            subject,
            body,
            EMAIL_HOST_USER,
            ['illanesluis18@gmail.com']
        )
        email.content_subtype = 'html'
        email.send(fail_silently=False)
        
    except Exception as e:
        print(f"Error al enviar el correo: {e}")