FROM python:3.14.5-slim-trixie

# Install OpenJDK 21
RUN apt update \
    && apt install -y --no-install-recommends openjdk-21-jdk-headless \
    && apt clean \
    && rm -rf /var/lib/apt/lists/*