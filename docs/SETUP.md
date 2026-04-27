# Deployment Setup Guide

Two Contabo VPS servers — dev (`dev.prescreen-app.com`) and prod (`prescreen-app.com`).

| Server | Environment | Domain |
|---|---|---|
| Contabo VPS 1 | Dev + GitHub Actions runner | `dev.prescreen-app.com` |
| Contabo VPS 2 | Production | `prescreen-app.com` |

---

## Before You Start

You need on your **local machine**:
- Terminal with SSH client
- Git
- GitHub account with access to the repo

Contabo will have emailed you root passwords for both servers. Find those emails before starting.

---

## Step 1 — Generate SSH Key (local machine)

This key lets GitHub Actions deploy to the prod server automatically. Run once on your local machine:

```bash
ssh-keygen -t ed25519 -f ~/.ssh/prescreen_deploy -C "github-actions" -N ""
```

Print both parts — keep this terminal open, you'll need them later:

```bash
echo "=== PRIVATE KEY (goes to GitHub) ===" && cat ~/.ssh/prescreen_deploy
echo "=== PUBLIC KEY (goes to prod server) ===" && cat ~/.ssh/prescreen_deploy.pub
```

---

## Step 2 — DNS Records

Log into your domain registrar. Add three A records for `prescreen-app.com`:

| Type | Host | Value | TTL |
|---|---|---|---|
| A | `@` | `<prod server IP>` | 3600 |
| A | `www` | `<prod server IP>` | 3600 |
| A | `dev` | `<dev server IP>` | 3600 |

Find your server IPs in Contabo Customer Control Panel → Your Services.

> **Do this first** — DNS takes 15 min to 2 hours to propagate. Continue with everything else while waiting.

Check propagation later with:

```bash
dig +short prescreen-app.com         # must return prod IP
dig +short dev.prescreen-app.com     # must return dev IP
```

---

## Step 3 — Contabo Object Storage

1. Log in to Contabo CCP → **Your Services** → **Object Storage** → create a new instance
2. Choose the same region as your servers
3. Once created, open the instance detail page — the **endpoint URL** is shown there
4. Find S3 credentials: look for an **Access Keys** or **Credentials** tab on the instance page,
   or under **Account → Security → API Credentials**
   (the exact location varies by CCP version — ask Contabo support chat if you can't find it)
5. Save these three values somewhere safe:
   - Endpoint URL (e.g. `https://eu2.contabostorage.com`)
   - Access key
   - Secret key

---

## Step 4 — Both Servers: Base Setup

Run the following on **each server** (dev and prod). SSH in with the root password from Contabo's email:

```bash
ssh root@<server-ip>
```

### 4.1 Update system

```bash
apt update && apt upgrade -y
apt install -y git curl ufw openssl nano unzip

# AWS CLI v2 (awscli apt package removed in Ubuntu 24.04)
curl -fsSL "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o /tmp/awscliv2.zip \
  && unzip /tmp/awscliv2.zip -d /tmp \
  && /tmp/aws/install \
  && rm -rf /tmp/awscliv2.zip /tmp/aws \
  && aws --version
```

### 4.2 Install Docker

```bash
curl -fsSL https://get.docker.com | sh
systemctl enable --now docker
docker --version    # confirms: Docker version 27.x or similar
```

### 4.3 Configure firewall

```bash
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP (certbot + redirect)
ufw allow 443/tcp   # HTTPS
ufw allow 7880/tcp  # LiveKit WebSocket
ufw allow 7881/udp  # LiveKit WebRTC media
ufw --force enable
ufw status
```

Expected output:
```
Status: active
22/tcp   ALLOW IN   Anywhere
80/tcp   ALLOW IN   Anywhere
443/tcp  ALLOW IN   Anywhere
7880/tcp ALLOW IN   Anywhere
7881/udp ALLOW IN   Anywhere
```

### 4.4 Create deploy user

```bash
useradd -m -s /bin/bash deploy
usermod -aG docker deploy
mkdir -p /home/deploy/.ssh
cp ~/.ssh/authorized_keys /home/deploy/.ssh/
chown -R deploy:deploy /home/deploy/.ssh
chmod 700 /home/deploy/.ssh
chmod 600 /home/deploy/.ssh/authorized_keys
```

### 4.5 Clone repository

Replace `achilovbakhrom` with your GitHub org or username:

```bash
git clone https://github.com/achilovbakhrom/hr_prescan.git /opt/prescreen
```

If the repo is private, use a personal access token:

```bash
git clone https://YOUR_TOKEN@github.com/achilovbakhrom/hr_prescan.git /opt/prescreen
```

---

## Step 5 — Dev Server: Full Setup

All commands in this section run on the **dev server only**.

### 5.1 Create github-runner user

```bash
useradd -m -s /bin/bash github-runner
usermod -aG docker github-runner
chown -R github-runner:github-runner /opt/prescreen
```

### 5.2 Generate all secrets

Run this block in one go. It prints every random secret you need:

```bash
echo "POSTGRES_PASSWORD=$(openssl rand -base64 32 | tr -d '=+/')"
echo "REDIS_PASSWORD=$(openssl rand -base64 32 | tr -d '=+/')"
echo "RABBITMQ_PASS=$(openssl rand -base64 32 | tr -d '=+/')"
echo "DJANGO_SECRET_KEY=$(openssl rand -base64 50 | tr -d '=+/')"
echo "S3_ACCESS_KEY=$(openssl rand -hex 16)"
echo "S3_SECRET_KEY=$(openssl rand -base64 32 | tr -d '=+/')"
echo "LIVEKIT_API_KEY=$(openssl rand -hex 16)"
echo "LIVEKIT_API_SECRET=$(openssl rand -base64 32 | tr -d '=+/')"
echo "INTERNAL_API_KEY=$(openssl rand -hex 32)"
echo "TELEGRAM_HR_WEBHOOK_SECRET=$(openssl rand -hex 20)"
echo "TELEGRAM_CANDIDATE_WEBHOOK_SECRET=$(openssl rand -hex 20)"
```

Copy the output to a text editor — you'll paste the values into the .env file next.

### 5.3 Create the .env file

```bash
cp /opt/prescreen/backend/.env.example /opt/prescreen/backend/.env
nano /opt/prescreen/backend/.env
```

> **Important:** The `REDIS_URL` and `RABBITMQ_URL` fields must contain the **actual password text**,
> not a variable like `${REDIS_PASSWORD}`. Docker does not interpolate variables inside .env files.

Fill in every value using the secrets generated above:

```bash
# === DOMAIN ===
DOMAIN=dev.prescreen-app.com
GITHUB_REPOSITORY=achilovbakhrom/hr_prescan
ALLOWED_HOSTS=dev.prescreen-app.com
CORS_ALLOWED_ORIGINS=https://dev.prescreen-app.com

# === DATABASE ===
POSTGRES_DB=hr_prescan_dev
POSTGRES_USER=hr_prescan_dev
POSTGRES_PASSWORD=paste_generated_value_here
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# === DJANGO ===
DJANGO_SECRET_KEY=paste_generated_value_here
DJANGO_SETTINGS_MODULE=config.settings.production

# === REDIS — paste the same password in both lines ===
REDIS_PASSWORD=paste_generated_value_here
REDIS_URL=redis://:paste_SAME_password_here@redis:6379/0

# === RABBITMQ — paste the same password in both lines ===
RABBITMQ_USER=hr_prescan
RABBITMQ_PASS=paste_generated_value_here
RABBITMQ_URL=amqp://hr_prescan:paste_SAME_password_here@rabbitmq:5672//

# === MINIO / S3 — S3_ and MINIO_ must hold the same values ===
S3_ACCESS_KEY=paste_generated_value_here
S3_SECRET_KEY=paste_generated_value_here
MINIO_ACCESS_KEY=paste_same_S3_ACCESS_KEY_here
MINIO_SECRET_KEY=paste_same_S3_SECRET_KEY_here
MINIO_ENDPOINT=http://minio:9000
MINIO_BUCKET_NAME=hr-prescan-dev

# === LIVEKIT ===
LIVEKIT_API_KEY=paste_generated_value_here
LIVEKIT_API_SECRET=paste_generated_value_here
LIVEKIT_URL=wss://dev.prescreen-app.com/ws/

# === AI SERVICES — fill in when you have the keys ===
GOOGLE_API_KEY=
DEEPGRAM_API_KEY=
ELEVENLABS_API_KEY=
ELEVENLABS_VOICE_ID=VEWZvLXUrFL3O7dUnBSW

# === TELEGRAM — fill in after Step 9 (Telegram bots) ===
TELEGRAM_HR_BOT_TOKEN=
TELEGRAM_HR_BOT_USERNAME=
TELEGRAM_HR_WEBHOOK_SECRET=paste_generated_value_here
TELEGRAM_HR_WEBHOOK_URL=https://dev.prescreen-app.com/api/telegram/hr/webhook/
TELEGRAM_CANDIDATE_BOT_TOKEN=
TELEGRAM_CANDIDATE_BOT_USERNAME=
TELEGRAM_CANDIDATE_WEBHOOK_SECRET=paste_generated_value_here
TELEGRAM_CANDIDATE_WEBHOOK_URL=https://dev.prescreen-app.com/api/telegram/candidate/webhook/

# === EMAIL ===
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=PreScreen Dev <noreply@dev.prescreen-app.com>

# === OTHER ===
GOOGLE_CLIENT_ID=
BILLING_ENABLED=False
INTERNAL_API_KEY=paste_generated_value_here
```

Save: `Ctrl+O` → Enter → `Ctrl+X`

Create the project-root `.env` for Docker Compose variable substitution:

```bash
cat > /opt/prescreen/.env << EOF
DOMAIN=dev.prescreen-app.com
GITHUB_REPOSITORY=achilovbakhrom/hr_prescan
IMAGE_TAG=dev
EOF
```

### 5.4 Backup configuration

```bash
mkdir -p /etc/hr_prescan

cat > /etc/hr_prescan/backup.env << EOF
POSTGRES_DB=hr_prescan_dev
POSTGRES_USER=hr_prescan_dev
PGPASSWORD=paste_your_POSTGRES_PASSWORD_here
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
DOCKER_CONTAINER=prescreen-postgres-1
BACKUP_DIR=/var/backups/hr_prescan
S3_BACKUP_ENDPOINT=paste_contabo_endpoint_here
S3_BACKUP_BUCKET=prescreen-backups
S3_BACKUP_ACCESS_KEY=paste_contabo_access_key_here
S3_BACKUP_SECRET_KEY=paste_contabo_secret_key_here
EOF

chmod 600 /etc/hr_prescan/backup.env
bash /opt/prescreen/deploy/scripts/backup-cron-setup.sh
```

### 5.5 SSL Certificate

First confirm DNS has propagated:

```bash
dig +short dev.prescreen-app.com    # must return dev server IP before continuing
```

Once it returns the correct IP:

```bash
cd /opt/prescreen

# Start nginx only (needed to serve the certbot ACME challenge)
IMAGE_TAG=dev docker compose \
  -f docker-compose.yml \
  -f deploy/docker-compose.prod.yml \
  -f deploy/docker-compose.staging.yml \
  up -d nginx

sleep 5

# Obtain the certificate
docker run --rm \
  -v /etc/letsencrypt:/etc/letsencrypt \
  -v /var/www/certbot:/var/www/certbot \
  certbot/certbot certonly \
    --webroot --webroot-path=/var/www/certbot \
    --email admin@prescreen-app.com \
    --agree-tos --no-eff-email \
    -d dev.prescreen-app.com

# Stop nginx — it will be started properly in Step 10
docker compose \
  -f docker-compose.yml \
  -f deploy/docker-compose.prod.yml \
  -f deploy/docker-compose.staging.yml \
  down
```

Expected output ends with:
```
Successfully received certificate.
Certificate is saved at: /etc/letsencrypt/live/dev.prescreen-app.com/fullchain.pem
```

### 5.6 GitHub Actions Runner

**Get the registration token from GitHub first** — it expires in 1 hour, so complete the next steps immediately.

1. Go to your repo → **Settings** → **Actions** → **Runners** → **New self-hosted runner**
2. Select **Linux** / **x64**
3. GitHub shows a download URL and a token — copy the **token** (looks like `AXXXXXXXXXX...`)

Do NOT use the token shown here — get a fresh one from the GitHub page.

**Back on the dev server:**

```bash
su - github-runner
mkdir ~/actions-runner && cd ~/actions-runner

# Paste the exact download URL shown in the GitHub UI — example:
curl -o actions-runner-linux-x64.tar.gz -L \
  https://github.com/actions/runner/releases/download/v2.323.0/actions-runner-linux-x64-2.323.0.tar.gz

tar xzf ./actions-runner-linux-x64.tar.gz

# Configure — paste YOUR token from GitHub
./config.sh \
  --url https://github.com/achilovbakhrom/hr_prescan \
  --token PASTE_TOKEN_HERE \
  --name prescreen-dev \
  --labels self-hosted,dev-server \
  --work _work \
  --unattended

exit    # back to root

cd /home/github-runner/actions-runner
./svc.sh install github-runner
./svc.sh start
systemctl status "actions.runner.*"    # should show: active (running)
```

Go to GitHub → Settings → Actions → Runners. The runner should appear as **Idle**.

---

## Step 6 — Prod Server: Full Setup

All commands in this section run on the **prod server only**.

### 6.1 Add the deploy SSH public key

This is the public key generated in Step 1:

```bash
echo "paste_full_contents_of_prescreen_deploy.pub_here" >> /home/deploy/.ssh/authorized_keys
```

Test it from your **local machine**:

```bash
ssh -i ~/.ssh/prescreen_deploy deploy@<prod-server-ip> echo "SSH works"
# Must print: SSH works — with no password prompt
```

### 6.2 Generate all secrets

Same as dev but run on the prod server. Use **different values from dev** — never share secrets between environments:

```bash
echo "POSTGRES_PASSWORD=$(openssl rand -base64 32 | tr -d '=+/')"
echo "REDIS_PASSWORD=$(openssl rand -base64 32 | tr -d '=+/')"
echo "RABBITMQ_PASS=$(openssl rand -base64 32 | tr -d '=+/')"
echo "DJANGO_SECRET_KEY=$(openssl rand -base64 50 | tr -d '=+/')"
echo "S3_ACCESS_KEY=$(openssl rand -hex 16)"
echo "S3_SECRET_KEY=$(openssl rand -base64 32 | tr -d '=+/')"
echo "LIVEKIT_API_KEY=$(openssl rand -hex 16)"
echo "LIVEKIT_API_SECRET=$(openssl rand -base64 32 | tr -d '=+/')"
echo "INTERNAL_API_KEY=$(openssl rand -hex 32)"
echo "TELEGRAM_HR_WEBHOOK_SECRET=$(openssl rand -hex 20)"
echo "TELEGRAM_CANDIDATE_WEBHOOK_SECRET=$(openssl rand -hex 20)"
```

### 6.3 Create the .env file

```bash
cp /opt/prescreen/backend/.env.example /opt/prescreen/backend/.env
nano /opt/prescreen/backend/.env
```

```bash
# === DOMAIN ===
DOMAIN=prescreen-app.com
GITHUB_REPOSITORY=achilovbakhrom/hr_prescan
ALLOWED_HOSTS=prescreen-app.com,www.prescreen-app.com
CORS_ALLOWED_ORIGINS=https://prescreen-app.com,https://www.prescreen-app.com

# === DATABASE ===
POSTGRES_DB=hr_prescan_prod
POSTGRES_USER=hr_prescan_prod
POSTGRES_PASSWORD=paste_prod_value_here
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# === DJANGO ===
DJANGO_SECRET_KEY=paste_prod_value_here
DJANGO_SETTINGS_MODULE=config.settings.production

# === REDIS ===
REDIS_PASSWORD=paste_prod_value_here
REDIS_URL=redis://:paste_SAME_password_here@redis:6379/0

# === RABBITMQ ===
RABBITMQ_USER=hr_prescan
RABBITMQ_PASS=paste_prod_value_here
RABBITMQ_URL=amqp://hr_prescan:paste_SAME_password_here@rabbitmq:5672//

# === MINIO / S3 ===
S3_ACCESS_KEY=paste_prod_value_here
S3_SECRET_KEY=paste_prod_value_here
MINIO_ACCESS_KEY=paste_same_S3_ACCESS_KEY_here
MINIO_SECRET_KEY=paste_same_S3_SECRET_KEY_here
MINIO_ENDPOINT=http://minio:9000
MINIO_BUCKET_NAME=hr-prescan

# === LIVEKIT ===
LIVEKIT_API_KEY=paste_prod_value_here
LIVEKIT_API_SECRET=paste_prod_value_here
LIVEKIT_URL=wss://prescreen-app.com/ws/

# === AI SERVICES ===
GOOGLE_API_KEY=
DEEPGRAM_API_KEY=
ELEVENLABS_API_KEY=
ELEVENLABS_VOICE_ID=VEWZvLXUrFL3O7dUnBSW

# === TELEGRAM — production bots only (created in Step 9) ===
TELEGRAM_HR_BOT_TOKEN=
TELEGRAM_HR_BOT_USERNAME=hr_prescreen_ai_bot
TELEGRAM_HR_WEBHOOK_SECRET=paste_prod_value_here
TELEGRAM_HR_WEBHOOK_URL=https://prescreen-app.com/api/telegram/hr/webhook/
TELEGRAM_CANDIDATE_BOT_TOKEN=
TELEGRAM_CANDIDATE_BOT_USERNAME=candidate_preview_ai_bot
TELEGRAM_CANDIDATE_WEBHOOK_SECRET=paste_prod_value_here
TELEGRAM_CANDIDATE_WEBHOOK_URL=https://prescreen-app.com/api/telegram/candidate/webhook/

# === EMAIL ===
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=PreScreen AI <noreply@prescreen-app.com>

# === OTHER ===
GOOGLE_CLIENT_ID=
BILLING_ENABLED=False
INTERNAL_API_KEY=paste_prod_value_here
```

Create the project-root `.env`:

```bash
cat > /opt/prescreen/.env << EOF
DOMAIN=prescreen-app.com
GITHUB_REPOSITORY=achilovbakhrom/hr_prescan
IMAGE_TAG=latest
EOF
```

### 6.4 Backup configuration

```bash
mkdir -p /etc/hr_prescan

cat > /etc/hr_prescan/backup.env << EOF
POSTGRES_DB=hr_prescan_prod
POSTGRES_USER=hr_prescan_prod
PGPASSWORD=paste_your_POSTGRES_PASSWORD_here
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
DOCKER_CONTAINER=prescreen-postgres-1
BACKUP_DIR=/var/backups/hr_prescan
S3_BACKUP_ENDPOINT=paste_contabo_endpoint_here
S3_BACKUP_BUCKET=prescreen-backups
S3_BACKUP_ACCESS_KEY=paste_contabo_access_key_here
S3_BACKUP_SECRET_KEY=paste_contabo_secret_key_here
EOF

chmod 600 /etc/hr_prescan/backup.env
bash /opt/prescreen/deploy/scripts/backup-cron-setup.sh
```

### 6.5 SSL Certificate

```bash
dig +short prescreen-app.com        # must return prod IP
dig +short www.prescreen-app.com    # must return prod IP
```

Once both return the correct IP:

```bash
cd /opt/prescreen

DOMAIN=prescreen-app.com \
EMAIL=admin@prescreen-app.com \
COMPOSE_FILE="docker-compose.yml -f deploy/docker-compose.prod.yml" \
bash deploy/scripts/init-letsencrypt.sh
```

Expected output ends with: `Certificate issued for prescreen-app.com`

---

## Step 7 — GitHub Environments

Go to your repo → **Settings** → **Environments**.

### Create `development` environment

Click **New environment** → name: `development` → **Configure environment**

Add **Environment variables** (not secrets):

| Name | Value |
|---|---|
| `DEV_DOMAIN` | `dev.prescreen-app.com` |
| `DEV_DEPLOY_PATH` | `/opt/prescreen` |

### Create `production` environment

Click **New environment** → name: `production` → **Configure environment**

Add **Environment secrets:**

| Name | Value |
|---|---|
| `PROD_SSH_KEY` | Full contents of `~/.ssh/prescreen_deploy` (private key — starts with `-----BEGIN OPENSSH PRIVATE KEY-----`) |
| `PROD_HOST` | prod server IP address |
| `PROD_USER` | `deploy` |
| `PROD_DEPLOY_PATH` | `/opt/prescreen` |

Add **Environment variables:**

| Name | Value |
|---|---|
| `DOMAIN` | `prescreen-app.com` |

---

## Step 8 — Telegram Bots

You need 4 bots total: HR and Candidate for each environment.

1. Open Telegram → search `@BotFather` → `/start`
2. Send `/newbot`
3. Enter a display name, e.g. `PreScreen Dev HR`
4. Enter a username, e.g. `prescreen_dev_hr_bot` (must end in `bot`)
5. BotFather replies with a token like `7123456789:AAHxxxxxxxxxxxxxxxx`
6. Repeat for all 4 bots

| Bot | Username example | Goes to |
|---|---|---|
| Dev HR | `prescreen_dev_hr_bot` | dev server `TELEGRAM_HR_BOT_TOKEN` |
| Dev Candidate | `prescreen_dev_candidate_bot` | dev server `TELEGRAM_CANDIDATE_BOT_TOKEN` |
| Prod HR | `hr_prescreen_ai_bot` | prod server `TELEGRAM_HR_BOT_TOKEN` |
| Prod Candidate | `candidate_preview_ai_bot` | prod server `TELEGRAM_CANDIDATE_BOT_TOKEN` |

After creating bots, update the `.env` files on each server with the tokens, then restart Django:

```bash
# On dev server
cd /opt/prescreen
docker compose \
  -f docker-compose.yml \
  -f deploy/docker-compose.prod.yml \
  -f deploy/docker-compose.staging.yml \
  restart django celery-worker
```

---

## Step 9 — First Deploy: Dev

The server is set up. The app deployment is fully automated — trigger it by pushing to the `dev` branch.

**On your local machine:**

```bash
git checkout dev
git commit --allow-empty -m "chore: trigger first dev deploy"
git push origin dev
```

Go to GitHub → **Actions** → **CD — Deploy to Dev** and watch the pipeline.
It will build images, push to GHCR, pull them on the dev server, run migrations, and collect static files automatically.

Wait for the pipeline to go green (~5–8 minutes on first run).

**After the pipeline succeeds — create the admin user** (one time only, on the dev server):

```bash
docker compose \
  -f /opt/prescreen/docker-compose.yml \
  -f /opt/prescreen/deploy/docker-compose.prod.yml \
  -f /opt/prescreen/deploy/docker-compose.staging.yml \
  exec django python manage.py createsuperuser
```

Run the smoke test:

```bash
bash /opt/prescreen/deploy/scripts/smoke-test.sh https://dev.prescreen-app.com
```

Expected final line: `All smoke tests passed.`

---

## Step 10 — First Deploy: Prod Server

The prod server is never deployed to manually — the CI/CD pipeline handles everything. Trigger it by pushing to `main`.

On your local machine:

```bash
git checkout main
git commit --allow-empty -m "chore: trigger first prod deploy"
git push origin main
```

Go to **GitHub → Actions → CD — Deploy to Production** and watch the pipeline.

It will:
1. Build and push Docker images tagged `:sha` and `:latest`
2. SSH into the prod server, pull images, run migrations, collectstatic
3. Rolling-update Django (scale 2→1), restart Celery, reload nginx
4. Run the smoke test against `https://prescreen-app.com`

**After the pipeline succeeds** — create the admin user (one time only, on the prod server):

```bash
ssh deploy@<PROD_IP>
docker compose \
  -f /opt/prescreen/docker-compose.yml \
  -f /opt/prescreen/deploy/docker-compose.prod.yml \
  exec django python manage.py createsuperuser
```

---

## Step 11 — Test CI/CD Pipelines

### Dev pipeline

On your local machine:

```bash
git checkout dev
git commit --allow-empty -m "chore: test dev pipeline"
git push origin dev
```

Go to GitHub → **Actions** → **CD — Deploy to Dev** → watch it run. Should go green in ~5 minutes.

### Prod pipeline

```bash
git checkout main
git merge dev
git push origin main
```

Go to GitHub → **Actions** → **CD — Deploy to Production** → watch it run.

---

## Step 12 — Test Backups

Run on each server:

```bash
# Run backup manually
bash /opt/prescreen/deploy/scripts/backup-db.sh

# Check the local dump was created
ls -lh /var/backups/hr_prescan/daily/

# Check the log
tail -30 /var/backups/hr_prescan/backup.log
```

The log should end with `S3 upload and rotation complete.` if Contabo Object Storage is configured correctly.

---

## Quick Reference

### Compose shortcuts (add to `~/.bashrc` on each server)

```bash
# Dev server
alias dcd='docker compose -f /opt/prescreen/docker-compose.yml \
  -f /opt/prescreen/deploy/docker-compose.prod.yml \
  -f /opt/prescreen/deploy/docker-compose.staging.yml'

# Prod server
alias dcp='docker compose -f /opt/prescreen/docker-compose.yml \
  -f /opt/prescreen/deploy/docker-compose.prod.yml'
```

After adding, run `source ~/.bashrc`. Then:

```bash
dcd ps                              # list services
dcd logs -f django                  # tail django logs
dcd restart django                  # restart a service
dcd exec django python manage.py shell  # Django shell
df -h && docker system df           # check disk usage
```

### Common fixes

**Container keeps restarting:**
```bash
docker logs <container-name> --tail 50
```

**Nginx 502 bad gateway:**
```bash
# Django not healthy yet — check
docker logs prescreen-django-1 --tail 30
```

**SSL cert not found:**
```bash
ls /etc/letsencrypt/live/    # should list your domain folder
```

**Runner went offline:**
```bash
systemctl restart "actions.runner.*"
```

---

## Full Checklist

```
[ ] Step 1  — SSH key pair generated locally
[ ] Step 2  — DNS A records added for @, www, dev
[ ] Step 3  — Contabo Object Storage bucket created, credentials saved
[ ] Step 4  — Both servers: Docker installed, ufw configured, deploy user created, repo cloned
[ ] Step 5  — Dev: github-runner user, .env filled, backup cron, SSL cert, runner installed + Idle in GitHub
[ ] Step 6  — Prod: deploy SSH key added and tested, .env filled, backup cron, SSL cert
[ ] Step 7  — GitHub: development + production environments with all secrets and variables
[ ] Step 8  — 4 Telegram bots created, tokens added to .env files on each server
[ ] Step 9  — Dev first deploy: all containers healthy, smoke test passed
[ ] Step 10 — Prod first deploy: all containers healthy, smoke test passed
[ ] Step 11 — Dev CI/CD: pushed to dev branch, pipeline completed green
[ ] Step 12 — Prod CI/CD: pushed to main, pipeline completed green
[ ] Step 13 — Backup test: ran backup-db.sh on both servers, S3 upload confirmed in log
```
