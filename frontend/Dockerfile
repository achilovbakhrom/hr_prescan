# Stage 1: Build
FROM node:22-slim AS build

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
# Skip TS check in image build — ci.yml handles vue-tsc.
# Building tolerantly so deploys aren't blocked by TS warnings.
RUN npx vite build

# Stage 2: Serve
FROM nginx:1.27-alpine AS production

COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
