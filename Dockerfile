FROM python:3-alpine
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache
WORKDIR /app
COPY pyproject.toml poetry.lock bin/entrypoint.sh ./
COPY rss2telegram ./rss2telegram
RUN touch README.md && \
    apk update && \
    apk add --no-cache python3 poetry && \
    poetry install --without test,docs,dev && \
    rm -rf $POETRY_CACHE_DIR README.md pyproject.toml poetry.lock && \
    apk del poetry && \
    addgroup -S appgroup && \
    adduser -S appuser -G appgroup && \
    mkdir database && \
    chown -R appuser:appgroup database && \
    chmod +x entrypoint.sh
USER appuser
HEALTHCHECK CMD sh -c "ps aux" | sh -c "grep [e]ntrypoint"
ENV PATH=".venv/bin:$PATH"
CMD [ "./entrypoint.sh" ]
