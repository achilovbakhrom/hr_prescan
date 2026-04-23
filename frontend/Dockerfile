# Stage 1: Build
FROM node:22-slim AS build

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

# Build-time config — Vite bakes these into the bundle. Override via --build-arg.
ARG VITE_API_URL=https://dev.prescreen-app.com/api
ARG VITE_LIVEKIT_URL=wss://dev.prescreen-app.com/ws/
ARG VITE_GOOGLE_CLIENT_ID=
ARG VITE_TELEGRAM_BOT_USERNAME=
ARG VITE_TELEGRAM_BOT_ID=
ARG VITE_TELEGRAM_CANDIDATE_BOT_USERNAME=
ARG VITE_TELEGRAM_HR_BOT_USERNAME=
ARG VITE_BILLING_ENABLED=false

RUN printf "VITE_API_URL=%s\nVITE_LIVEKIT_URL=%s\nVITE_GOOGLE_CLIENT_ID=%s\nVITE_TELEGRAM_BOT_USERNAME=%s\nVITE_TELEGRAM_BOT_ID=%s\nVITE_TELEGRAM_CANDIDATE_BOT_USERNAME=%s\nVITE_TELEGRAM_HR_BOT_USERNAME=%s\nVITE_BILLING_ENABLED=%s\n" \
  "$VITE_API_URL" "$VITE_LIVEKIT_URL" "$VITE_GOOGLE_CLIENT_ID" \
  "$VITE_TELEGRAM_BOT_USERNAME" "$VITE_TELEGRAM_BOT_ID" \
  "$VITE_TELEGRAM_CANDIDATE_BOT_USERNAME" "$VITE_TELEGRAM_HR_BOT_USERNAME" "$VITE_BILLING_ENABLED" \
  > .env.production

# Skip TS check in image build — ci.yml handles vue-tsc.
RUN npx vite build

# Stage 2: Serve
FROM nginx:1.27-alpine AS production

COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
