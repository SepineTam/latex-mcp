FROM texlive/texlive:latest-full

# 安装中文字体和 Python
RUN apt-get update && \
    apt-get install -y \
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
