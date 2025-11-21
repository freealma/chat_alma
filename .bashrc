# Build and run Alma CLI Docker container
alias build_alma='docker build -t alma-cli .'

# Use Alma CLI with Docker
alias alma='docker run -it --env-file .env -v $(pwd)/db:/alma/db alma-cli'

# Comand to export all tables from alma.db to CSV files
alias copy_tables='
#!/bin/bash

DB_PATH="/alma/db/alma.db"
OUTPUT_DIR="/alma/data"

# Crear directorio de salida si no existe
mkdir -p "$OUTPUT_DIR"

# Obtener lista de tablas
tables=$(sqlite3 "$DB_PATH" ".tables")

# Exportar cada tabla a CSV
for table in $tables; do
    echo "Exportando tabla: $table"
    sqlite3 -header -csv "$DB_PATH" "SELECT * FROM $table;" > "$OUTPUT_DIR/${table}.csv"
done

echo "Exportación completada. Archivos guardados en: $OUTPUT_DIR"'