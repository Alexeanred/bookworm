#!/bin/bash

echo "Waiting for PostgreSQL to be ready..."
sleep 10

echo "Importing data into bookworm database..."
# Sử dụng Docker để chạy lệnh psql
docker exec -i bookworm-db psql -U postgres -d bookworm < bookworm_localhost-2025_04_24_18_57_48-dump.sql

echo "Data import completed"
