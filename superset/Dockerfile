FROM apache/superset:3.0.1

USER root

# Bypass SSL inspection and install the required PostgreSQL driver
RUN pip install --no-cache-dir --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org psycopg2-binary

COPY superset_config.py /app/pythonpath/superset_config.py

# Generate the init script inline to absolutely prevent Windows CRLF/BOM issues
RUN { \
    echo '#!/bin/bash'; \
    echo 'echo "=== Starting Superset Initialization ==="'; \
    echo 'superset fab create-admin --username admin --firstname System --lastname Administrator --email admin@telephony-monitor.com --password admin'; \
    echo 'superset db upgrade'; \
    echo 'superset init'; \
    echo 'echo "=== Initialization complete. Starting Gunicorn server... ==="'; \
    echo 'exec gunicorn -w 2 --timeout 120 -b 0.0.0.0:8088 "superset.app:create_app()"'; \
} > /app/init-system.sh && chmod +x /app/init-system.sh

USER superset

ENTRYPOINT ["/app/init-system.sh"]
