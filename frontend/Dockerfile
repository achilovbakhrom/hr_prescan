# Stage 1: Dependencies
FROM node:22-slim AS deps

WORKDIR /app

COPY package.json yarn.lock ./
RUN corepack enable && yarn install --frozen-lockfile

# Stage 2: Build
FROM deps AS build

COPY . .

# Build-time config — Nuxt/Vite exposes these to the client bundle. Override via --build-arg.
ARG VITE_API_URL=https://dev.prescreen-app.com/api
ARG VITE_LIVEKIT_URL=wss://dev.prescreen-app.com/ws/
ARG VITE_GOOGLE_CLIENT_ID=
ARG VITE_TELEGRAM_BOT_USERNAME=
ARG VITE_TELEGRAM_BOT_ID=
ARG VITE_TELEGRAM_CANDIDATE_BOT_USERNAME=
ARG VITE_TELEGRAM_HR_BOT_USERNAME=
ARG VITE_BILLING_ENABLED=false
ARG VITE_GA_MEASUREMENT_ID=

ENV VITE_API_URL=$VITE_API_URL
ENV VITE_LIVEKIT_URL=$VITE_LIVEKIT_URL
ENV VITE_GOOGLE_CLIENT_ID=$VITE_GOOGLE_CLIENT_ID
ENV VITE_TELEGRAM_BOT_USERNAME=$VITE_TELEGRAM_BOT_USERNAME
ENV VITE_TELEGRAM_BOT_ID=$VITE_TELEGRAM_BOT_ID
ENV VITE_TELEGRAM_CANDIDATE_BOT_USERNAME=$VITE_TELEGRAM_CANDIDATE_BOT_USERNAME
ENV VITE_TELEGRAM_HR_BOT_USERNAME=$VITE_TELEGRAM_HR_BOT_USERNAME
ENV VITE_BILLING_ENABLED=$VITE_BILLING_ENABLED
ENV VITE_GA_MEASUREMENT_ID=$VITE_GA_MEASUREMENT_ID

# Skip TS check in image build — ci.yml handles `nuxt typecheck`.
RUN yarn build
RUN if [ -n "$VITE_GA_MEASUREMENT_ID" ]; then grep -R "$VITE_GA_MEASUREMENT_ID" .output >/dev/null; fi

# Stage 3: Serve
FROM node:22-slim AS production

WORKDIR /app

ENV NODE_ENV=production
ENV NITRO_HOST=0.0.0.0
ENV NITRO_PORT=3000

COPY --from=build /app/.output ./.output

EXPOSE 3000

CMD ["node", ".output/server/index.mjs"]
