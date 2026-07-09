Ferremas

Este es un proyecto de e-commerce para ferreteria Ferremas

Requisitos

- Python 3.12 o superior
- pip
- Virtualenv

Instalación

1. Clona el repositorio:

   
    git clone https://github.com/Vasycs/ferr_e_mas.git
   cd ferremas
   

2. Crea y activa un entorno virtual:

   
   python -m venv env
   source env/bin/activate  # En Windows usa `env\Scripts\activate`
   

3. Instala las dependencias:

   
   pip install -r requirements.txt

   Nota: Pillow está incluido en `requirements.txt`.

4. Configura las variables de entorno:

   - Crea un archivo `.env` en la raíz del proyecto con las siguientes variables:

     
     SECRET_KEY=tu_secreto
     EMAIL_HOST_USER=tu_correo@gmail.com
     EMAIL_HOST_PASSWORD=tu_contraseña
     

5. Realiza las migraciones:

   
   python manage.py migrate
   

6. Ejecuta el servidor:

   
   python manage.py runserver
   

Uso

Accede a `http://127.0.0.1:8000/` en tu navegador para ver el proyecto en funcionamiento.

- usuario test de venta:

user: testventa
pass: abcd1234

- superuser test:

user: abrah
pass: abraham15

- tarjeta de prueba
- 4051 8856 0044 6623
- CVV 123
- cualquier fecha de expiración
- RUT 11.111.111-1
- clave 123

Contacto

Si tienes preguntas o sugerencias, no dudes en abrir un issue o contactar al desarrollador.

---
