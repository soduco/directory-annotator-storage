FROM python:3.7-slim-buster
# Python deps
COPY . /tmp/directory_annotator_storage

RUN pip install -q --no-cache-dir \
    --use-pep517 /tmp/directory_annotator_storage gunicorn \
    && rm -rf /tmp/directory_annotator_storage

# Install curl to support healthcheck
RUN apt-get update && \
    apt-get install -y curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/

# HEALTHCHECK --interval=5s --timeout=3s \
#   CMD curl -f http://localhost:8000/health_check || exit 1

ENV LC_ALL=C
WORKDIR /app
CMD gunicorn --timeout 500 --access-logfile - --bind 0.0.0.0:8000 --proxy-allow-from='*' 'directory_annotator_storage:create_app()'

