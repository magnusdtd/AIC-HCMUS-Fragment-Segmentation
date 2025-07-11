# Build Frontend
FROM node:18-alpine AS frontend-builder

WORKDIR /frontend

COPY ./frontend/package*.json ./
RUN npm ci

COPY ./frontend ./
RUN npm run build

WORKDIR /app


FROM node:18-alpine AS frontend

WORKDIR /app

RUN npm install -g serve

COPY --from=frontend-builder /frontend/dist ./build

EXPOSE 8070

CMD ["serve", "-s", "build", "-l", "8070"]

