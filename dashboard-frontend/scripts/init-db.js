require('dotenv').config();
const { sql } = require('@vercel/postgres');
const { readFileSync } = require('fs');
const { join } = require('path');

async function initializeDatabase() {
    try {
        // Read the schema file
        const schemaPath = join(process.cwd(), 'src', 'lib', 'schema.sql');
        const schema = readFileSync(schemaPath, 'utf8');

        // Execute the schema
        console.log('Creating database tables...');
        await sql.query(schema);
        console.log('Database tables created successfully!');

    } catch (error) {
        console.error('Error initializing database:', error);
        process.exit(1);
    } finally {
        process.exit(0);
    }
}

initializeDatabase(); 
