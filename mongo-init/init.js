print("Initializing MongoDB...");

db = db.getSiblingDB("airflow");

db.createCollection("standard_ok");
db.createCollection("standard_ko");

print("Database 'airflow' and collections created successfully!");