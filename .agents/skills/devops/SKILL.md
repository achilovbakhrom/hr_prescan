---
name: devops
description: Operate the HR PreScan dev and prod servers — SSH, container health, logs, deploy status, env var changes, backups, and the Contabo API. Use when the user asks about server state, a deploy, a production issue, or any "ssh into…" / "check on the server…" / "restart…" / "pull logs…" request.
user-invocable: true
---

# DevOps Skill

Hands-on operations for the HR PreScan infrastructure. Two servers, same shape:

| Env  | Host env var          | Role                                              |
|------|-----------------------|---------------------------------------------------|
| Dev  | `$PRESCAN_DEV_HOST`   | `dev.prescreen-app.com` — auto-deploys from `dev` branch |
| Prod | `$PRESCAN_PROD_HOST`  | `prescreen-app.com` — auto-deploys from `main` branch |

Both are self-hosted GitHub Actions runners. The `cd-dev.yml` / `cd.yml` workflows run `docker compose` **on the server itself**. Credentials are stored in `.Codex/settings.local.json` under `env`:
- `PRESCAN_DEV_HOST`, `PRESCAN_DEV_USER`, `PRESCAN_DEV_PASSWORD`
- `PRESCAN_PROD_HOST`, `PRESCAN_PROD_USER`, `PRESCAN_PROD_PASSWORD`
- `CONTABO_CLIENT_ID`, `CONTABO_CLIENT_SECRET`
- `CONTABO_S3_ACCESS_KEY`, `CONTABO_S3_SECRET_KEY`

Never echo these values back to the user in output — reference them by name only.

## Safety rules (non-negotiable)

1. **Prod is different.** Any command that mutates prod state (restart container, change env, delete anything, `docker system prune`, `docker volume rm`, `systemctl stop`, `truncate`, `DROP`, `DELETE FROM`) needs **explicit user confirmation for that specific command** before executing. A prior "yes, proceed" on a different task does not carry over.
2. **Read-only first.** When diagnosing, default to `docker ps`, `docker logs --tail`, `df -h`, `free -m`, `top -b -n 1`, `journalctl --since`, `ls`, `cat`. Write actions only after you understand what's broken.
3. **Never log credentials.** Do not `env | grep PRESCAN`, `cat .env`, or dump full compose configs. If you must read an env var on the server, read the specific key with `grep '^VAR_NAME=' .env`.
4. **Secrets stay on the server.** Don't copy `.env` files back to the laptop or paste contents into conversation.
5. **Don't bypass the auto-deploy.** If code needs to change on the server, push to `dev`/`main` — don't SSH in and edit files under `${DEV_DEPLOY_PATH}`. That directory is a `git reset --hard` mirror of the branch; local edits get wiped on next deploy.
6. **No force-push / destructive git on servers.** The deploy path uses `reset --hard`; that's the workflow's prerogative, not yours.

## SSH pattern (password auth via sshpass)

Both servers use root + password (no keys yet). Use `sshpass` with `-e` so the password is passed via env var, not the command line:

```bash
# Dev — read-only example
SSHPASS="$PRESCAN_DEV_PASSWORD" sshpass -e ssh -o StrictHostKeyChecking=accept-new \
  "$PRESCAN_DEV_USER@$PRESCAN_DEV_HOST" 'docker ps --format "table {{.Names}}\t{{.Status}}"'

# Prod — same shape
SSHPASS="$PRESCAN_PROD_PASSWORD" sshpass -e ssh -o StrictHostKeyChecking=accept-new \
  "$PRESCAN_PROD_USER@$PRESCAN_PROD_HOST" 'df -h /'
```

`-o StrictHostKeyChecking=accept-new` adds the host key on first connect but refuses changed keys (protects against MITM if the host key rotates unexpectedly).

For multi-line remote commands, wrap the remote side in single-quoted heredoc-free syntax; if you need a heredoc, escape `$` vars you want to expand on the server side and unescape the ones you want expanded locally.

**Recommend key-based auth once.** After the first successful connect, offer to run `ssh-copy-id` to install the user's local pubkey so future sessions don't need the password. That's a one-time setup the user has to accept — don't do it silently.

## Standard operations

### 1. Check service health
```bash
ssh … 'cd ${DEPLOY_PATH} && docker compose \
  -f docker-compose.yml \
  -f deploy/docker-compose.prod.yml \
  -f deploy/docker-compose.staging.yml ps'
```
For **prod** drop the `staging.yml` override (it's dev-only — resource caps). The deploy path is in the GitHub env vars (`DEV_DEPLOY_PATH` / `PROD_DEPLOY_PATH`). If you don't know it, `ls /root /opt /srv | head` usually surfaces it quickly.

### 2. Tail container logs
```bash
ssh … 'docker compose logs --tail=200 --timestamps django'
ssh … 'docker logs --tail=200 --timestamps <container-name>'
```
Services to know: `django`, `celery-worker`, `celery-beat`, `nginx`, `postgres`, `redis`, `rabbitmq`, `livekit`, `livekit-agent`, `minio`.

### 3. Restart one service (graceful)
```bash
ssh … 'cd ${DEPLOY_PATH} && IMAGE_TAG=<sha> docker compose … up -d --no-deps --wait <service>'
```
For celery workers use `stop` first to drain tasks (`docker compose … stop celery-worker`), then `up -d`. `cd-dev.yml` already does this — mirror that pattern.

### 4. Change an env var
Edit the server's deploy `.env` (usually alongside the compose files):
```bash
ssh … 'cd ${DEPLOY_PATH} && grep -n "^ALLOW_E2E_HOOKS=" .env || echo "not set"'
ssh … 'cd ${DEPLOY_PATH} && sed -i "s|^EXISTING_KEY=.*|EXISTING_KEY=new_value|" .env'
# then restart only the services that consume the var
ssh … 'cd ${DEPLOY_PATH} && docker compose … up -d --no-deps django'
```
For adding a **new** variable, `echo "KEY=value" >> .env` — but first confirm the key isn't already present.

### 5. Database ops (Django)
```bash
ssh … 'cd ${DEPLOY_PATH} && docker compose … exec django python manage.py shell_plus'
ssh … 'cd ${DEPLOY_PATH} && docker compose … exec -T django python manage.py dbshell'
ssh … 'cd ${DEPLOY_PATH} && docker compose … exec django python manage.py showmigrations --list | head -40'
```
Migrations run automatically via the backend `entrypoint.sh` on each container start — don't run `migrate` manually unless you're debugging a stuck migration.

### 6. Postgres backup (dev → local)
```bash
ssh … 'cd ${DEPLOY_PATH} && docker compose … exec -T postgres \
  pg_dump -U $POSTGRES_USER $POSTGRES_DB --format=custom' > /tmp/hr_prescan_dev.pgdump
```
For prod, confirm with the user first — dumping a large prod DB over SSH can be slow. Prefer the nightly backup in Contabo Object Storage if it exists.

### 7. Smoke test after a deploy
```bash
bash deploy/scripts/smoke-test.sh "https://dev.prescreen-app.com"
```
Run locally — no SSH needed. Scripts that hit the public domain.

## Contabo API (compute + storage)

**Auth flow** — OAuth2 password grant. Requires the Contabo account email + password **in addition to** the Client ID/Secret you already have. The `env` block only stores the API creds; user creds are prompted when needed (don't store them — they're the account's master password).

```bash
# Ask the user for their Contabo account email + password the first time,
# then hold them in a shell var for the session:
read -p "Contabo account email: " CONTABO_USER
read -sp "Contabo account password: " CONTABO_PASS; echo

TOKEN=$(curl -fsSL -X POST \
  'https://auth.contabo.com/auth/realms/contabo/protocol/openid-connect/token' \
  -d "client_id=$CONTABO_CLIENT_ID" \
  -d "client_secret=$CONTABO_CLIENT_SECRET" \
  -d "username=$CONTABO_USER" \
  -d "password=$CONTABO_PASS" \
  -d 'grant_type=password' | python3 -c 'import json,sys; print(json.load(sys.stdin)["access_token"])')
```

Common endpoints (`https://api.contabo.com/v1/...`):
- `GET /compute/instances` — list VPS instances (returns your two servers)
- `GET /compute/instances/{id}` — detailed state
- `POST /compute/instances/{id}/actions/restart` — soft reboot
- `POST /compute/instances/{id}/actions/shutdown` / `start`
- `POST /compute/instances/{id}/snapshots` — create snapshot (costs €, ask first)

Every request needs two headers:
```
Authorization: Bearer $TOKEN
x-request-id: $(uuidgen)
```

### Contabo Object Storage (S3-compatible)

Use `aws s3` with a custom endpoint. Endpoint URL depends on the region — read it from the backend's `.env`:
```bash
ssh … 'cd ${DEPLOY_PATH} && grep -E "^(MINIO_ENDPOINT|S3_ENDPOINT|AWS_S3_ENDPOINT)" .env'
```

Then locally:
```bash
AWS_ACCESS_KEY_ID="$CONTABO_S3_ACCESS_KEY" \
AWS_SECRET_ACCESS_KEY="$CONTABO_S3_SECRET_KEY" \
aws --endpoint-url=<endpoint-from-env> s3 ls s3://<bucket>/
```

If `aws` isn't available, `mc` (MinIO client) also works against any S3 endpoint.

## Workflow: "deploy to dev failed"

1. Check the GitHub Actions run: `gh run list --workflow cd-dev.yml --limit 5`.
2. If it's at the "Rolling update — backend" step, look at deploy container health:
   `ssh dev 'cd … && docker compose … ps'`.
3. Tail Django logs for the failure cause:
   `ssh dev 'docker compose … logs --tail=500 --timestamps django | tail -100'`.
4. If migrations failed, run `showmigrations` to see which one is pending.
5. If a rollback to `:dev` happened, the workflow logs say `[ROLLBACK] Done` — the old image is live but the bad commit is still on the `dev` branch. Push a fix commit; do **not** revert the deploy manually.

## Workflow: "something's on fire in prod"

Triage order:
1. `curl -s -o /dev/null -w "%{http_code}\n" https://prescreen-app.com/api/health/` — is it 200?
2. SSH and `docker compose … ps` — are all containers healthy?
3. `free -m && df -h /` — OOM or disk-full?
4. `docker compose … logs --tail=200 django | grep -iE "error|traceback|500|oom"` — app-level errors?
5. `docker compose … logs --tail=200 postgres` — DB issues?
6. Offer options (restart `django`, scale celery, etc.) and **ask before acting**. For prod, single-service restarts first; never `docker compose down`.

## What NOT to do (without explicit ask)

- `docker system prune` / `docker volume rm` / `docker network prune` — can destroy data.
- `rm -rf` anywhere under `/var/lib/docker/volumes` — data loss.
- `systemctl stop docker` — kills the whole stack.
- Edit files under the deploy path — they get wiped on next deploy (use branches).
- Paste server `.env` contents into the conversation.
- Rotate any of the stored creds without asking — the user keeps them synced to their own secret store.
