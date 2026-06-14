# ============================================================
# CarValueAI — React Frontend Dockerfile (Multi-Stage Build)
# ============================================================
#
# IMPORTANT: VITE_API_URL is compiled into the JS bundle at
# build time. If you change the backend URL later, you MUST
# rebuild this image with the new --build-arg:
#
#   docker build --build-arg VITE_API_URL=https://new-backend.com .
#
# A runtime env var change alone will NOT work because Vite
# inlines environment variables into the static bundle during
# "npm run build". This is by design (Vite docs).
# ============================================================

# ── Stage 1: Build the React app ──────────────────────────────
FROM node:20-alpine AS build

WORKDIR /app

# Build argument — must be passed at docker build time
ARG VITE_API_URL=http://localhost:8000
ENV VITE_API_URL=$VITE_API_URL

# Copy package files first for layer caching
COPY package.json package-lock.json* ./
RUN npm install

# Copy source code and build
COPY . .
RUN npm run build

# ── Stage 2: Serve with Nginx ────────────────────────────────
FROM nginx:alpine

# Copy built assets from the build stage
COPY --from=build /app/dist /usr/share/nginx/html

# Copy custom Nginx config for SPA routing
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
