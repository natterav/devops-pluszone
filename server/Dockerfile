FROM node:18

WORKDIR /app

# Copiar dependencias
COPY package*.json ./

RUN npm install

# Copiar todo
COPY . .

# Puerto de Express (ajústalo si usas otro)
EXPOSE 5000

CMD ["node", "index.js"]
