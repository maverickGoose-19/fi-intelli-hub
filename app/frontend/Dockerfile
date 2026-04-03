FROM node:20-alpine AS deps

WORKDIR /app
COPY app/frontend/package*.json ./
RUN npm ci

FROM node:20-alpine AS builder

WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY app/frontend ./
RUN mkdir -p public && npm run build

FROM node:20-alpine AS runner

ENV NODE_ENV=production \
    PORT=3000

WORKDIR /app

COPY --from=builder /app/package*.json ./
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/public ./public
COPY --from=builder /app/next.config.ts ./next.config.ts

EXPOSE 3000

CMD ["sh", "-c", "npx next start -H 0.0.0.0 -p ${PORT}"]
