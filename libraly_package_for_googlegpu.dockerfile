# 必要なパッケージの更新とインストール
!apt-get update

# Chrome for Testingのインストール
!wget https://storage.googleapis.com/chrome-for-testing-public/129.0.6668.58/linux64/chrome-linux64.zip -N -P /tmp
!unzip -o /tmp/chrome-linux64.zip -d /tmp/
!cp -rf /tmp/chrome-linux64 /usr/local/bin/chrome-linux64
!ln -s /usr/local/bin/chrome-linux64/chrome /usr/local/bin/google-chrome

# ChromeDriver for Testingのインストール
!wget https://storage.googleapis.com/chrome-for-testing-public/129.0.6668.58/linux64/chromedriver-linux64.zip -N -P /tmp
!unzip -o /tmp/chromedriver-linux64.zip -d /tmp/
!cp -rf /tmp/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver

# 既存のパッケージのインストール
!apt-get install -y ffmpeg
!pip uninstall -y torch
!pip install torch==2.0.1+cu118 torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu118
!pip install selenium-wire
!pip install moviepy
!pip install jaconv
!pip install soundfile
!pip install argostranslate
!pip install git+https://github.com/openai/whisper.git
!pip install numpy
