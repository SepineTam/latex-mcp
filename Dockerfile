FROM ubuntu:22.04

RUN apt-get update &&  \
    apt-get install -y \
    texlive-full \
    fonts-noto-cjk \
    fonts-wqy-zenhei \
    fonts-wqy-microhei \
    curl \
    && fc-cache -fv \
    && rm -rf /var/lib/apt/lists/*

# 安装uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

COPY . /app
WORKDIR /app
RUN uv sync

WORKDIR /workspace

ENTRYPOINT ["/app/.venv/bin/latex-mcp"]
