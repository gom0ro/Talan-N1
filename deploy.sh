#!/bin/bash
# ═══════════════════════════════════════════════════════════
#  Talant №1 — Deployment Script
#  Server: 89.46.33.230
#  Domain: talant.inbrain.kz
#  Stack:  Nginx + Gunicorn + Django
# ═══════════════════════════════════════════════════════════

set -e  # Қате болса, тоқтау

# ─── VARIABLES ────────────────────────────────────────────
APP_NAME="talant"
DOMAIN="talant.inbrain.kz"
PROJECT_DIR="/var/www/$APP_NAME"
VENV_DIR="$PROJECT_DIR/venv"
USER="www-data"
DJANGO_SETTINGS="project.settings_prod"

echo "══════════════════════════════════════════════"
echo "  🚀 Talant №1 — Deployment бастау"
echo "══════════════════════════════════════════════"

# ─── 1. SYSTEM UPDATE ────────────────────────────────────
echo ""
echo "📦 [1/8] Қажетті пакеттерді орнату..."
apt update
apt install -y python3 python3-pip python3-venv nginx curl

# ─── 2. PROJECT DIRECTORY ────────────────────────────────
echo ""
echo "📁 [2/8] Жоба каталогын жасау..."
mkdir -p $PROJECT_DIR
mkdir -p $PROJECT_DIR/media
mkdir -p $PROJECT_DIR/staticfiles

# ─── 3. COPY PROJECT FILES ──────────────────────────────
# Файлдар rsync арқылы жіберілгенін болжаймыз
if [ ! -f "$PROJECT_DIR/manage.py" ]; then
    echo ""
    echo "⚠️  МАҢЫЗДЫ: Файлдар серверге көшірілмеген!"
    echo "   Серверге файлдарды жібергеннен кейін осы скриптті қайта орындаңыз."
    echo ""
    echo "   Файлдарды жіберу командасы (Локальді компьютерден):"
    echo "   rsync -avz --exclude='.git' --exclude='__pycache__' --exclude='venv' --exclude='*.pyc' . root@89.46.33.230:$PROJECT_DIR/"
    echo ""
    exit 1
fi

# ─── 4. VIRTUAL ENVIRONMENT ─────────────────────────────
echo ""
echo "🐍 [3/8] Python виртуалды ортасын жасау..."
python3 -m venv $VENV_DIR
source $VENV_DIR/bin/activate
pip install --upgrade pip
pip install -r $PROJECT_DIR/requirements.txt

# ─── 5. DJANGO SETUP ────────────────────────────────────
echo ""
echo "⚙️  [4/8] Django орнату..."
cd $PROJECT_DIR
export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS

python manage.py migrate --noinput
python manage.py collectstatic --noinput

# Суперпайдаланушы бар ма тексеру
echo "from django.contrib.auth.models import User; print('Admin exists' if User.objects.filter(is_superuser=True).exists() else 'No admin')" | python manage.py shell 2>/dev/null | grep -q "No admin" && {
    echo ""
    echo "👤 Суперпайдаланушы жоқ. Жасаймыз..."
    python manage.py createsuperuser --noinput --username admin --email admin@talant.inbrain.kz 2>/dev/null || true
    echo "   ⚠️  Пароль орнату: python manage.py changepassword admin"
}

# ─── 6. GUNICORN SERVICE ────────────────────────────────
echo ""
echo "🦄 [5/8] Gunicorn сервисін жасау..."
cat > /etc/systemd/system/gunicorn-$APP_NAME.service << 'GUNICORN_EOF'
[Unit]
Description=Gunicorn daemon for Talant №1
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/talant
Environment="DJANGO_SETTINGS_MODULE=project.settings_prod"
ExecStart=/var/www/talant/venv/bin/gunicorn project.wsgi:application \
    --workers 3 \
    --bind unix:/var/www/talant/gunicorn.sock \
    --access-logfile /var/log/gunicorn-talant-access.log \
    --error-logfile /var/log/gunicorn-talant-error.log \
    --timeout 120

[Install]
WantedBy=multi-user.target
GUNICORN_EOF

# Артна процесті қосу
systemctl daemon-reload
systemctl enable gunicorn-$APP_NAME
systemctl restart gunicorn-$APP_NAME

echo "   ✅ Gunicorn сервисі іске қосылды"

# ─── 7. NGINX CONFIG ────────────────────────────────────
echo ""
echo "🌐 [6/8] Nginx конфигурациясын жасау..."
cat > /etc/nginx/sites-available/$APP_NAME << NGINX_EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN 89.46.33.230;

    # Security headers
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;

    # Static files
    location /static/ {
        alias $PROJECT_DIR/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Media files
    location /media/ {
        alias $PROJECT_DIR/media/;
        expires 7d;
    }

    # Favicon
    location /favicon.ico {
        alias $PROJECT_DIR/staticfiles/img/favicon.ico;
        access_log off;
        log_not_found off;
    }

    # Django via Gunicorn
    location / {
        proxy_pass http://unix:$PROJECT_DIR/gunicorn.sock;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 300s;
        proxy_read_timeout 300s;
        client_max_body_size 50M;
    }
}
NGINX_EOF

# Конфигурацияны іске қосу
ln -sf /etc/nginx/sites-available/$APP_NAME /etc/nginx/sites-enabled/

# Конфигурацияны тексеру
nginx -t

echo "   ✅ Nginx конфигурациясы дайын"

# ─── 8. FILE PERMISSIONS ────────────────────────────────
echo ""
echo "🔐 [7/8] Файл рұқсаттарын орнату..."
chown -R www-data:www-data $PROJECT_DIR
chmod -R 755 $PROJECT_DIR
chmod -R 775 $PROJECT_DIR/media
chmod 664 $PROJECT_DIR/db.sqlite3
chown www-data:www-data $PROJECT_DIR/db.sqlite3

# ─── 9. START SERVICES ──────────────────────────────────
echo ""
echo "🟢 [8/8] Сервистерді қайта іске қосу..."
systemctl restart gunicorn-$APP_NAME
nginx -s reload  # Басқа сайттарды тоқтатпай қайта жүктеу

# ─── DONE ────────────────────────────────────────────────
echo ""
echo "══════════════════════════════════════════════"
echo "  ✅ DEPLOYMENT СӘТТІ АЯҚТАЛДЫ!"
echo "══════════════════════════════════════════════"
echo ""
echo "  🌐 Сайт:   http://$DOMAIN"
echo "  🌐 IP:     http://89.46.33.230"
echo "  🔑 Админ:  http://$DOMAIN/admin/"
echo ""
echo "  📋 Пайдалы командалар:"
echo "     Статус:    systemctl status gunicorn-$APP_NAME"
echo "     Логтар:    journalctl -u gunicorn-$APP_NAME -f"
echo "     Рестарт:   systemctl restart gunicorn-$APP_NAME"
echo "     Nginx:     systemctl restart nginx"
echo ""
