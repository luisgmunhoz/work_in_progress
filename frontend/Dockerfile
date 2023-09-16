# Stage 1: Build the application
FROM node:18-alpine as build
WORKDIR /app

# Copy package.json and package-lock.json to the working directory
COPY package.json package-lock.json ./

# Install dependencies
RUN npm ci

# Copy the rest of the application code
COPY . .

# Build the application
RUN npm run build

# Stage 2: Serve the built application
FROM node:18-alpine as production
WORKDIR /app

# Copy the built files from the previous stage
COPY --from=build /app .

