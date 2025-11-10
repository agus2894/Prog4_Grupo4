# 🚨 GUÍA DE SOLUCIÓN DE ERRORES 500 EN RENDER

## 🔍 Cómo diagnosticar:

### 1. **Ver logs de Render:**
   - Dashboard Render > Tu servicio > Logs
   - Buscar líneas en rojo con "ERROR" o "CRITICAL"

### 2. **Errores comunes y soluciones:**

#### ❌ Error: "SECRET_KEY not found"
**Solución:** Agregar `SECRET_KEY` en Environment Variables de Render

#### ❌ Error: "could not connect to server: Connection refused"
**Solución:** 
- Verificar que `DATABASE_URL` esté configurado
- Asegurar que PostgreSQL esté vinculado al servicio

#### ❌ Error: "No such file or directory: '/staticfiles'"
**Solución:** 
- Verificar que `build.sh` se ejecute
- `python manage.py collectstatic --no-input` en build.sh

#### ❌ Error: "Invalid HTTP_HOST header"
**Solución:**
- Verificar `ALLOWED_HOSTS` en settings.py
- Debe incluir `RENDER_EXTERNAL_HOSTNAME`

#### ❌ Error: "relation 'auth_user' does not exist"
**Solución:**
- Ejecutar `python manage.py migrate` en build.sh
- Verificar que migraciones se apliquen

#### ❌ Error: "Site matching query does not exist"
**Solución:**
- El comando `setup_database` debe crear el sitio
- Verificar que se ejecute en build.sh

### 3. **Variables de entorno requeridas:**

```bash
# OBLIGATORIAS
SECRET_KEY=una-clave-secreta-muy-larga-y-aleatoria
DATABASE_URL=postgresql://user:password@host:port/dbname

# OAUTH (para login social)
GOOGLE_CLIENT_ID=tu-google-client-id
GOOGLE_CLIENT_SECRET=tu-google-client-secret
GITHUB_CLIENT_ID=tu-github-client-id
GITHUB_CLIENT_SECRET=tu-github-client-secret

# EMAIL (recomendado)
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-app-password
```

### 4. **Comandos de debug en Render:**

Si tienes acceso a shell en Render:
```bash
# Verificar migraciones
python manage.py showmigrations

# Verificar usuarios
python manage.py shell -c "from django.contrib.auth.models import User; print(User.objects.count())"

# Verificar sitios
python manage.py shell -c "from django.contrib.sites.models import Site; print(Site.objects.all())"

# Crear superusuario manualmente
python manage.py createsuperuser
```

### 5. **Estructura del build.sh correcta:**

```bash
#!/usr/bin/env bash
set -o errexit

echo "🚀 Iniciando deployment..."
pip install -r requirements.txt
python manage.py migrate --noinput
python manage.py collectstatic --noinput
python manage.py setup_database
echo "✅ Deployment completado!"
```