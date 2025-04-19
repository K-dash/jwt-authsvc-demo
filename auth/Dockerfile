FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONBUFFERED=1

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:0.5.1 /uv /uvx /bin/
WORKDIR /app/auth

ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never

COPY ./pyproject.toml ./uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=./uv.lock,target=./uv.lock \
    --mount=type=bind,source=./pyproject.toml,target=./pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

COPY auth app/auth

ENV PATH="/app/auth/.venv/bin:$PATH"

CMD ["bash"]
