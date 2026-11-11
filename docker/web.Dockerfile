FROM node:22-slim AS base
RUN corepack enable
WORKDIR /app/web
COPY web/package.json web/pnpm-lock.yaml web/pnpm-workspace.yaml ./
RUN pnpm install --frozen-lockfile

FROM base AS dev
USER node
CMD ["pnpm", "dev"]

FROM base AS build
COPY web/ ./
RUN pnpm build

FROM nginx:1.27-alpine AS prod
COPY --from=build /app/web/dist /usr/share/nginx/html
