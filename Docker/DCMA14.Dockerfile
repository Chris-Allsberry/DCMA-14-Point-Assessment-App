FROM python:3.14.5-slim-trixie

# Install OpenJDK 21
RUN apt update \
    && apt install -y --no-install-recommends openjdk-21-jdk-headless \
    && apt clean \
    && rm -rf /var/lib/apt/lists/*

# Set ENV for datapath
ENV INPUT_OUTPUT_PATH='/data'

# Create Directories
WORKDIR $INPUT_OUTPUT_PATH
WORKDIR /app

# Create Volume
Volume $INPUT_OUTPUT_PATH

# Copy
COPY ./src/dcma14pointassessor/* ./src/dcma14pointassessor/
COPY pyproject.toml .

# Build Install Build
RUN pip install build

# Build and Install WHL
RUN python3 -m build . \
    && pip install ./dist/*.whl

CMD ['dcma14']
