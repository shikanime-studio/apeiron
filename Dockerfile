	
ARG	PYTHON_VERSION=3.12
ARG	DEBIAN_VERSION=bookworm
FROM	ghcr.io/astral-sh/uv:python${PYTHON_VERSION}-${DEBIAN_VERSION}-slim	AS	builder
ENV	UV_COMPILE_BYTECODE	1	UV_LINK_MODE	copy
ENV	UV_PYTHON_DOWNLOADS	0
WORKDIR	/app
RUN	uv sync --frozen --no-install-project --no-dev
COPY	pyproject.toml	uv.lock	/app/
COPY	apeiron/	/app/apeiron/
RUN	uv sync --frozen --no-dev
FROM	python:${PYTHON_VERSION}-slim-${DEBIAN_VERSION}
LABEL	org.opencontainers.image.source="https://github.com/shikanime-studio/apeiron"
LABEL	org.opencontainers.image.description="Apeiron AI"
LABEL	org.opencontainers.image.licenses="AGPL-3.0"
WORKDIR	/app
COPY	/app	.
ENTRYPOINT	["/app/.venv/bin/uvicorn"]
CMD	["--factory","apeiron.app:create_app","--host","0.0.0.0"]
