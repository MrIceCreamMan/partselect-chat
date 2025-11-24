FROM node:18-alpine

WORKDIR /app

# Install dependencies first (better caching)
COPY package*.json ./
RUN if [ -f package-lock.json ]; then npm ci; else npm install; fi

# Copy source (compose bind-mount will override in dev)
COPY . .

# Environment tuned for CRA in Docker
ENV NODE_ENV=development \
    CHOKIDAR_USEPOLLING=true \
    WATCHPACK_POLLING=true \
    BROWSER=none \
    HOST=0.0.0.0 \
    PORT=3000

EXPOSE 3000

# CRA dev server
CMD ["npm", "start"]