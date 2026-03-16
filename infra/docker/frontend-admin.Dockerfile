FROM node:20-alpine AS build

WORKDIR /app

COPY apps/frontend/admin/package*.json ./
RUN npm install

COPY apps/frontend/admin ./
RUN npm run build

FROM nginx:stable-alpine
COPY --from=build /app/dist /usr/share/nginx/html
