#!/bin/bash

# Change to the dashboard-frontend directory
cd dashboard-frontend

# Install dependencies if needed
npm install

# Build the project
npm run build

# Deploy to Vercel
npx vercel --prod

echo "Frontend deployment completed!" 