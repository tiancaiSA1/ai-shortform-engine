# 创建专用临时目录
mkdir -p /data/pip-tmp

# 设置环境变量，让 pip 使用这个目录
export TMPDIR=/data/pip-tmp
export TEMP=/data/pip-tmp
export TMP=/data/pip-tmp

python3.10 -m pip install --target ./python -r requirements.txt
python3.10 -m pip install --target ./python --no-deps blind_watermark

zip -r my-layer-code.zip python
sudo rm -r python/