FROM node:18.12.1-bullseye-slim

# Set working directory
WORKDIR /app

# Copy package.json and package-lock.json first
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of your app
COPY . .

# Expose port your app runs on
EXPOSE 3000

# Start the application
CMD ["node", "app.js"]
