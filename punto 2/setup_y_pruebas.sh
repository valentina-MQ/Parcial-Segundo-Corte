#!/usr/bin/env bash
set -e

ANTLR_JAR="antlr-4.13.2-complete.jar"
DIR="$(cd "$(dirname "$0")" && pwd)"

echo "--- Configuración de NoQL (Entorno Virtual) ---"

# 1. Generar Lexer y Parser (Java)
echo "→ Generando Lexer y Parser (Python3)..."
java -cp "$DIR/$ANTLR_JAR" org.antlr.v4.Tool -Dlanguage=Python3 -visitor "$DIR/NoQL.g4" -o "$DIR"

# 2. Crear y configurar el entorno virtual
if [ ! -d "$DIR/venv" ]; then
    echo "→ Creando entorno virtual..."
    python3 -m venv "$DIR/venv"
fi

# 3. Instalar dependencias en el venv
echo "→ Instalando antlr4-python3-runtime en el venv..."
"$DIR/venv/bin/pip" install antlr4-python3-runtime==4.13.2 -q

# 4. Ejecutar pruebas usando el Python del venv
echo "→ Ejecutando pruebas_noql.py..."
echo ""
"$DIR/venv/bin/python3" "$DIR/pruebas_noql.py"