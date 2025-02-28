FROM amazonlinux:2

# Copy requirements.txt
COPY . /src

# Install dependencies
RUN yum install -y \
    tar \
    xz \
    zip \
    python3 \
    glibc \
    glibc-common \
    glibc-devel \
    glibc-headers \
    libstdc++ \
    gzip \
    mesa-libGL \
    && yum clean all \
    && rm -rf /var/cache/yum

# Install pip
RUN python3 -m ensurepip --upgrade

# Set PYTHONPATH to include the custom install directory
ENV PYTHONPATH="/opt/python:${PYTHONPATH}"

# Install Python dependencies to /opt/python
RUN pip3 install --target /opt/python -r /src/requirements.txt

# Install FFmpeg
RUN curl -L -o ffmpeg.tar.xz https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-i686-static.tar.xz \
    && mkdir -p /opt/ffmpeg \
    && tar -xf ffmpeg.tar.xz --strip-components=1 -C /opt/ffmpeg \
    && rm ffmpeg.tar.xz

# Create Lambda layer package
RUN mkdir -p /opt/python/bin \
    && cp /opt/ffmpeg/ffmpeg /opt/python/bin/ \
    && cd /opt \
    && zip -r9 /opt/ffmpeg_layer.zip python

# Set entry point (for local testing, not needed in Lambda)
ENTRYPOINT [ "/bin/sh" ]
