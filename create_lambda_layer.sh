mkdir -p ffmpeg-layer/python/lib/python3.9/site-packages
cd ffmpeg-layer

# Download FFmpeg static build for Amazon Linux 2
curl -O https://johnvansickle.com/ffmpeg/builds/ffmpeg-git-amd64-static.tar.xz
tar xf ffmpeg-git-amd64-static.tar.xz
mv ffmpeg-git-*/ffmpeg python/

# Install Python dependencies
pip install -t python/lib/python3.9/site-packages pydicom Pillow

# Create ZIP for Lambda layer
zip -r ffmpeg_layer.zip python/
