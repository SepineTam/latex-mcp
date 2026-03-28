FROM texlive/texlive:latest-full

# Note:
# By using this image, you agree to the license terms of bundled software.

# Install commonly used fonts.
# Some font package names vary across Debian/Ubuntu releases and architectures,
# so we install only packages that are available in the current APT index.
RUN set -eux; \
    apt-get update; \
    FONT_PACKAGES="\
      fonts-noto-cjk \
      fonts-noto-cjk-extra \
      fonts-wqy-zenhei \
      fonts-wqy-microhei \
      fonts-dejavu \
      fonts-dejavu-extra \
      fonts-liberation \
      fonts-liberation2 \
      fonts-noto-core \
      fonts-noto-extra \
      fonts-noto-ui-core \
      fonts-noto-ui-extra \
      fonts-noto-mono \
      fonts-roboto \
      fonts-open-sans \
      fonts-lato \
      fonts-montserrat \
      fonts-firacode \
      fonts-jetbrains-mono \
      fonts-source-code-pro \
      fonts-inconsolata \
      fonts-noto-color-emoji \
      fonts-crosextra-carlito \
      fonts-crosextra-caladea \
      fonts-freefont-otf \
      fonts-ibm-plex\
    "; \
    AVAILABLE_PACKAGES=""; \
    for pkg in $FONT_PACKAGES; do \
      if apt-cache show "$pkg" >/dev/null 2>&1; then \
        AVAILABLE_PACKAGES="$AVAILABLE_PACKAGES $pkg"; \
      else \
        echo "Skipping unavailable font package: $pkg"; \
      fi; \
    done; \
    apt-get install -y --no-install-recommends $AVAILABLE_PACKAGES curl; \
    fc-cache -fv; \
    rm -rf /var/lib/apt/lists/*

# Install uv.
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

COPY . /app
WORKDIR /app
RUN uv sync

WORKDIR /workspace

ENTRYPOINT ["/app/.venv/bin/latex-mcp"]
