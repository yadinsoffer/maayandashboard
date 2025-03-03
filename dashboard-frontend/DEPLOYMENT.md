# Deployment Guide

This Next.js application is set up to be deployed on Vercel. The main repository contains both the frontend and backend code, with the Next.js frontend located in the `dashboard-frontend` directory.

## Project Structure

- The Next.js application is in the `dashboard-frontend` directory
- The `@/` path alias points to `./src/` as defined in both `tsconfig.json` and `jsconfig.json`
- Important modules:
  - `@/lib/ec2-api.ts` - API client for EC2 operations
  - `@/lib/db.ts` - Database operations

## Vercel Deployment

When deploying to Vercel through GitHub:

1. Make sure the project settings in Vercel dashboard has the **Root Directory** set to `dashboard-frontend`
2. The `vercel.json` at the root level should contain:
   ```json
   {
     "framework": "nextjs",
     "installCommand": "cd dashboard-frontend && npm install",
     "buildCommand": "cd dashboard-frontend && npm run build",
     "outputDirectory": "dashboard-frontend/.next",
     "rewrites": [
       { "source": "/(.*)", "destination": "/dashboard-frontend/$1" }
     ]
   }
   ```

3. The `.vercelignore` file is used to ignore files outside the dashboard-frontend directory

## Common Issues

- **Module Resolution**: If modules like `@/lib/ec2-api` or `@/lib/db` can't be found during build, make sure:
  - The root directory is correctly set in Vercel
  - Path aliases are properly defined in both `tsconfig.json` and `jsconfig.json`
  - There are no conflicting configurations between local development and production builds 