FROM texlive/texlive:latest-full

# Notes：
# 使用本镜像即表示您同意其中所包含软件的使用条款

# 安装常用字体
RUN apt-get update && \
    apt-get install -y \
    # 中日韩字体
    fonts-noto-cjk \
    fonts-noto-cjk-extra \
    fonts-wqy-zenhei \
    fonts-wqy-microhei \
    # 西文字体
    fonts-dejavu \
    fonts-dejavu-extra \
    fonts-liberation \
    fonts-liberation2 \
    # 微软核心字体
    ttf-mscorefonts-installer \
    # 现代无衬线字体
    fonts-roboto \
    fonts-open-sans \
    fonts-lato \
    fonts-montserrat \
    # 编程等宽字体
    fonts-firacode \
    fonts-jetbrains-mono \
    fonts-source-code-pro \
    # Emoji 字体
    fonts-noto-color-emoji \
    # 其他常用字体
    fonts-crosextra-carlito \
    fonts-crosextra-caladea \
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
