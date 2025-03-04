FROM public.ecr.aws/lambda/python:3.8

# Install minimal dependencies
RUN yum install -y \
    wget \
    tar \
    xz \
    && yum clean all

# Install static FFmpeg
RUN curl -L -o ffmpeg.tar.xz https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-i686-static.tar.xz \
    && mkdir -p /opt/ffmpeg \
    && tar -xf ffmpeg.tar.xz --strip-components=1 -C /opt/ffmpeg \
    && rm ffmpeg.tar.xz \
    && ln -s /opt/ffmpeg/ffmpeg /usr/local/bin/ffmpeg \
    && ln -s /opt/ffmpeg/ffprobe /usr/local/bin/ffprobe

# Set FFmpeg environment variables
ENV PATH="/opt/ffmpeg:${PATH}"

# Copy function code and requirements
WORKDIR ${LAMBDA_TASK_ROOT}
COPY lambda_handler.py .
COPY utils.py .
COPY requirements.txt .

# Install Python dependencies
RUN pip install -r requirements.txt

# Set the CMD to your handler
CMD [ "lambda_handler.lambda_handler" ]
