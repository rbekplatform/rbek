FROM python:3.12-slim

ARG RBEK_VERSION=0.2.0
ARG RBEK_INSTALLER_URL=https://releases.rbekplatform.com/cli/stable/install.sh
ARG RBEK_INSTALLER_SHA256=0a3fabcad4c114c133b96cb71e1406d25279c2c05fa3b37f95a8e446a10b7c86

LABEL org.opencontainers.image.title="RBEK"
LABEL org.opencontainers.image.description="RBEK governed execution runtime"
LABEL org.opencontainers.image.version="0.2.0"
LABEL org.opencontainers.image.source="https://github.com/rbekplatform/rbek"
LABEL org.opencontainers.image.url="https://rbekplatform.com"
LABEL org.opencontainers.image.vendor="RBEK Platform"

RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends ca-certificates curl; \
    rm -rf /var/lib/apt/lists/*; \
    test -x /usr/local/bin/python3.12; \
    ln -sf /usr/local/bin/python3.12 /usr/bin/python3.12; \
    test -x /usr/bin/python3.12; \
    curl -fsSL "$RBEK_INSTALLER_URL" -o /tmp/rbek-install.sh; \
    echo "$RBEK_INSTALLER_SHA256  /tmp/rbek-install.sh" | sha256sum -c -; \
    chmod 700 /tmp/rbek-install.sh; \
    /tmp/rbek-install.sh; \
    rm -f /tmp/rbek-install.sh; \
    test "$(rbek-cli --version)" = "RBEK $RBEK_VERSION"

ENTRYPOINT ["rbek-cli"]
CMD ["--version"]
