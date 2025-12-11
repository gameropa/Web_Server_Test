# Install dependencies
FROM node:20-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm install

# Build
FROM node:20-alpine AS build
WORKDIR /app
# Inject public env vars at build time so Next.js embeds them
ARG NEXT_PUBLIC_NODE_API
ARG NEXT_PUBLIC_PY_API
ARG NEXT_PUBLIC_CS_API
ENV NEXT_TELEMETRY_DISABLED=1 \
	NEXT_PUBLIC_NODE_API=${NEXT_PUBLIC_NODE_API} \
	NEXT_PUBLIC_PY_API=${NEXT_PUBLIC_PY_API} \
	NEXT_PUBLIC_CS_API=${NEXT_PUBLIC_CS_API}
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

# Runtime
FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
ENV PORT=3003
COPY --from=build /app/.next ./.next
COPY --from=build /app/public ./public
COPY --from=build /app/package*.json ./
COPY --from=deps /app/node_modules ./node_modules
RUN npm prune --production
EXPOSE 3003
CMD ["npm", "run", "start", "--", "-p", "3003"]
