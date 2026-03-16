FROM texlive/texlive:latest-full

# Note:
# By using this image, you agree to the license terms of bundled software.

# Install commonly used fonts.
RUN apt-get update && \
    apt-get install -y \
    # CJK fonts
    fonts-noto-cjk \
    fonts-noto-cjk-extra \
    fonts-wqy-zenhei \
    fonts-wqy-microhei \
    # Latin fonts
    fonts-dejavu \
    fonts-dejavu-extra \
    fonts-liberation \
    fonts-liberation2 \
    # Additional Noto families
    fonts-noto-core \
    fonts-noto-extra \
    fonts-noto-ui-core \
    fonts-noto-ui-extra \
    fonts-noto-mono \
    # Modern sans-serif fonts
    fonts-roboto \
    fonts-open-sans \
    fonts-lato \
    fonts-montserrat \
    # Monospace fonts
    fonts-firacode \
    fonts-jetbrains-mono \
    fonts-source-code-pro \
    fonts-inconsolata \
    # Emoji fonts
    fonts-noto-color-emoji \
    # Other common fonts
    fonts-crosextra-carlito \
    fonts-crosextra-caladea \
    fonts-freefont-otf \
    fonts-ibm-plex \
    curl \
    && fc-cache -fv \
    && rm -rf /var/lib/apt/lists/*

# Install uv.
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

COPY . /app
WORKDIR /app
RUN uv sync

WORKDIR /workspace

ENTRYPOINT ["/app/.venv/bin/latex-mcp"]
