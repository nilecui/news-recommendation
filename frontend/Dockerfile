# Build stage
FROM node:18-alpine as build

WORKDIR /app

ENV http_proxy=http://192.168.12.82:10909
ENV https_proxy=http://192.168.12.82:10909


# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built assets from build stage
COPY --from=build /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port 80
EXPOSE 80

ENV http_proxy=
ENV https_proxy=

# Start nginx
CMD ["nginx", "-g", "daemon off;"]