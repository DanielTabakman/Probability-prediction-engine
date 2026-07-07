FROM node:20-alpine AS deps
WORKDIR /app
# better-sqlite3 (command-center + entitlements) needs native compile on Alpine
RUN apk add --no-cache python3 make g++
COPY package.json package-lock.json* ./
RUN npm ci

FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ARG NEXT_PUBLIC_MSOS_SIGN_IN_URL=https://app.marketstructureos.com
ARG NEXT_PUBLIC_PPE_RESEARCH_OFFER_URL=
ARG NEXT_PUBLIC_PPE_RESEARCH_OFFER_LABEL=
ARG NEXT_PUBLIC_PPE_EMBED_URL=
ENV NEXT_PUBLIC_MSOS_SIGN_IN_URL=$NEXT_PUBLIC_MSOS_SIGN_IN_URL
ENV NEXT_PUBLIC_PPE_RESEARCH_OFFER_URL=$NEXT_PUBLIC_PPE_RESEARCH_OFFER_URL
ENV NEXT_PUBLIC_PPE_RESEARCH_OFFER_LABEL=$NEXT_PUBLIC_PPE_RESEARCH_OFFER_LABEL
ENV NEXT_PUBLIC_PPE_EMBED_URL=$NEXT_PUBLIC_PPE_EMBED_URL
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
ENV PORT=3000
RUN apk add --no-cache su-exec
RUN addgroup --system --gid 1001 nodejs && adduser --system --uid 1001 nextjs
RUN mkdir -p /data && chown nextjs:nodejs /data
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
EXPOSE 3000
ENTRYPOINT ["sh", "/usr/local/bin/docker-entrypoint.sh"]
CMD ["node", "server.js"]
