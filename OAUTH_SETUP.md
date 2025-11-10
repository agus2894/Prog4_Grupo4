# 🔐 Guía de Configuración de Autenticación Social

Esta guía te explica cómo configurar la autenticación con Google y GitHub en tu aplicación Mercadito.

## 📋 Prerrequisitos

✅ Django-allauth ya está instalado y configurado  
✅ Templates de login y registro actualizados  
✅ URLs configuradas  

## 🔧 Configuración paso a paso

### 1. 🌐 Configurar Google OAuth

#### Paso 1: Crear proyecto en Google Console
1. Ve a [Google Developers Console](https://console.developers.google.com/)
2. Crea un nuevo proyecto o selecciona uno existente
3. Nombre del proyecto: "Mercadito" (o el que prefieras)

#### Paso 2: Habilitar APIs
1. Ve a "Biblioteca" en el menú lateral
2. Busca "Google+ API" y habilítala
3. También habilita "Google People API"

#### Paso 3: Crear credenciales OAuth
1. Ve a "Credenciales" en el menú lateral
2. Haz clic en "Crear credenciales" > "ID de cliente OAuth 2.0"
3. Si es la primera vez, configura la pantalla de consentimiento:
   - Tipo de usuario: Externo
   - Nombre de la aplicación: Mercadito
   - Email del usuario: tu email
   - Dominio autorizado: tu-app.onrender.com

#### Paso 4: Configurar ID de cliente OAuth
1. Tipo de aplicación: Aplicación web
2. Nombre: Mercadito Web Client
3. **Orígenes de JavaScript autorizados:**
   - `http://127.0.0.1:8000` (desarrollo)
   - `https://tu-app.onrender.com` (producción)
4. **URIs de redirección autorizados:**
   - `http://127.0.0.1:8000/accounts/google/login/callback/` (desarrollo)
   - `https://tu-app.onrender.com/accounts/google/login/callback/` (producción)

#### Paso 5: Obtener credenciales
1. Copia el **Client ID** y **Client Secret**
2. Guárdalos para configurar las variables de entorno

### 2. 🐙 Configurar GitHub OAuth

#### Paso 1: Crear OAuth App en GitHub
1. Ve a [GitHub Developer Settings](https://github.com/settings/developers)
2. Haz clic en "New OAuth App"

#### Paso 2: Configurar la aplicación
1. **Application name:** Mercadito
2. **Homepage URL:** 
   - Desarrollo: `http://127.0.0.1:8000`
   - Producción: `https://tu-app.onrender.com`
3. **Application description:** E-commerce con IA - Mercadito
4. **Authorization callback URL:**
   - Desarrollo: `http://127.0.0.1:8000/accounts/github/login/callback/`
   - Producción: `https://tu-app.onrender.com/accounts/github/login/callback/`

#### Paso 3: Obtener credenciales
1. Una vez creada, obtendrás el **Client ID**
2. Genera un **Client Secret**
3. Guárdalos para las variables de entorno

### 3. ⚙️ Configurar Variables de Entorno

#### Para desarrollo local (.env):
```bash
GOOGLE_CLIENT_ID=tu-google-client-id
GOOGLE_CLIENT_SECRET=tu-google-client-secret
GITHUB_CLIENT_ID=tu-github-client-id  
GITHUB_CLIENT_SECRET=tu-github-client-secret
```

#### Para Render (Environment Variables):
1. Ve a tu dashboard de Render
2. Selecciona tu servicio web
3. Ve a "Environment"
4. Agrega las variables:
   - `GOOGLE_CLIENT_ID`: tu-google-client-id
   - `GOOGLE_CLIENT_SECRET`: tu-google-client-secret
   - `GITHUB_CLIENT_ID`: tu-github-client-id
   - `GITHUB_CLIENT_SECRET`: tu-github-client-secret

### 4. 🗄️ Configurar aplicaciones sociales en Django Admin

Una vez que tengas el superusuario creado en Render:

1. Ve a `/admin/` en tu aplicación
2. Busca "Aplicaciones sociales" en la sección "Social accounts"
3. Agrega una nueva aplicación social para Google:
   - **Provider:** Google
   - **Name:** Google
   - **Client id:** tu-google-client-id
   - **Secret key:** tu-google-client-secret
   - **Sites:** Selecciona "example.com" (el sitio por defecto)

4. Agrega una nueva aplicación social para GitHub:
   - **Provider:** GitHub  
   - **Name:** GitHub
   - **Client id:** tu-github-client-id
   - **Secret key:** tu-github-client-secret
   - **Sites:** Selecciona "example.com"

## 🚀 Probar la configuración

### Desarrollo local:
1. Ejecuta: `python manage.py runserver`
2. Ve a `http://127.0.0.1:8000/accounts/login/`
3. Haz clic en "Continuar con Google" o "Continuar con GitHub"

### Producción en Render:
1. Asegúrate de que todas las variables de entorno están configuradas
2. Ve a tu URL de Render `/accounts/login/`
3. Prueba los botones de autenticación social

## 🔍 Solución de problemas comunes

### Error: "redirect_uri_mismatch"
- Verifica que las URLs de callback coincidan exactamente
- Asegúrate de incluir el `/` al final de las URLs

### Error: "invalid_client"  
- Verifica que el Client ID y Secret sean correctos
- Revisa que las aplicaciones sociales estén configuradas en Django Admin

### Error: "Application not found"
- Asegúrate de que las aplicaciones sociales estén creadas en Django Admin
- Verifica que el Site ID sea correcto (generalmente 1)

### Los usuarios no se crean automáticamente
- Verifica que `SOCIALACCOUNT_AUTO_SIGNUP = True` esté en settings.py
- Revisa que el adaptador personalizado esté configurado

## 🎉 ¡Listo!

Una vez configurado todo correctamente, los usuarios podrán:
- Iniciar sesión con Google o GitHub
- Registrarse automáticamente con sus datos sociales
- Tener perfiles automáticamente creados
- Disfrutar de una experiencia de login fluida y moderna

¡Tu Mercadito ahora tiene autenticación social profesional! 🛒✨