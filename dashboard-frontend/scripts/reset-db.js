require('dotenv').config();
const { sql } = require('@vercel/postgres');
const { readFileSync } = require('fs');
const { join } = require('path');

async function resetDatabase() {
    try {
        // Drop existing tables
        console.log('Dropping existing tables...');
        await sql`DROP TABLE IF EXISTS daily_metrics CASCADE`;
        await sql`DROP TABLE IF EXISTS metrics CASCADE`;
        
        // Read and execute the schema
        console.log('Creating tables...');
        const schemaPath = join(process.cwd(), 'src', 'lib', 'schema.sql');
        const schema = readFileSync(schemaPath, 'utf8');
        await sql.query(schema);
        
        console.log('Database reset successfully!');
    } catch (error) {
        console.error('Error resetting database:', error);
        process.exit(1);
    } finally {
        process.exit(0);
    }
}

resetDatabase(); 