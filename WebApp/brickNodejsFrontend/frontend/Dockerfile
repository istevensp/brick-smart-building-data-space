# Use official Node image
FROM node:20-alpine

# Set working directory inside the container
WORKDIR /app

# Copy dependency files
COPY package.json package-lock.json ./

# Install dependencies
RUN npm install

# Copy the rest of the app
COPY . .

# Expose React dev server port
EXPOSE 3000

# Start the dev server
CMD ["npm", "start"]
