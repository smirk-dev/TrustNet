FROM node:18.20.2-alpine3.14

# Update package index and upgrade packages to patch vulnerabilities
RUN apk update && apk upgrade --no-cache

# Optionally, run a vulnerability scan after building the image

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy application code
COPY src/ ./src/

# Create non-root user
RUN addgroup -g 1001 -S nodejs
RUN adduser -S trustnet -u 1001

USER trustnet

EXPOSE 8080

CMD ["npm", "start"]
