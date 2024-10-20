import os
import time
from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service
from datetime import datetime
import subprocess
from moviepy.editor import VideoFileClip
import jaconv
import json
import wave
import soundfile as sf
import io
import numpy as np
import re
import argostranslate.package
import argostranslate.translate
import whisper  # Whisperライブラリのインポート

# 日本語をアルファベット表記に変換する関数
def convert_to_alphabet(text):
    return jaconv.kana2alphabet(text)

# Argos Translateを使って日本語を英語に翻訳する関数
def translate_text(text, from_lang="ja", to_lang="en"):
    installed_languages = argostranslate.translate.get_installed_languages()

    # 翻訳元言語と翻訳先言語を探す
    from_language = next(filter(lambda x: x.code == from_lang, installed_languages), None)
    to_language = next(filter(lambda x: x.code == to_lang, installed_languages), None)

    if from_language is None or to_language is None:
        raise Exception(f"言語パッケージが見つかりません。'{from_lang}' または '{to_lang}' の言語パッケージをインストールしてください。")

    # 翻訳を実行
    translated_text = from_language.get_translation(to_language).translate(text)
    return translated_text

# スペースで分割されている単語を整理する関数
def clean_text(text):
    text = re.sub(r'(\w+)\s(\w+)', r'\1\2', text)  # ひらがなと漢字が分かれている箇所を修正
    text = re.sub(r'(\d+)\s(\w+)', r'\1\2', text)  # 数字と単位の間のスペースを修正
    text = re.sub(r'\s+', ' ', text)  # 不要な複数の空白を1つにする
    text = re.sub(r'(?<=\d)(\s)(?=\d)', '', text)  # 数字同士のスペースを削除
    return text

# 句読点や改行を追加して自然な文章にする関数
def format_text(text):
    # 文末の句点の後に改行を追加して日本語の文章を整形
    text = re.sub(r'。', '。\n', text)  # "。" の後に改行を追加
    text = re.sub(r'(が|で|と|を|に|へ)(\s)', r'\1、', text)  # 文の区切りに読点を追加
    return text

# 英語用の改行を追加して整形する関数
def format_english_text(text):
    # 文末のピリオドの後に改行を追加して英語の文章を整形
    text = re.sub(r'\.(\s*)', '.\n', text)  # ピリオドの後に改行を追加
    return text

# ビデオリンクを取得する関数
def extract_video_link():
    # URLをファイルから読み込む
    with open('/content/drive/MyDrive/Mokkorikomori/erningvideo/target.txt', 'r') as file:
        url = file.read().strip()

    # 読み込んだURLを表示
    print(f"読み込んだURL: {url}")

    # 処理開始時間を記録
    start_time = time.time()

    # ChromeOptionsを設定して、ヘッドレスモードを有効化
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')  # ヘッドレスモード
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    # Chrome for Testingのバイナリのパスを指定
    chrome_options.binary_location = '/usr/local/bin/chrome-linux64/chrome'

    # ChromeDriverのパスを指定
    service = Service('/usr/local/bin/chromedriver')

    # WebDriverを作成
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Selenium Wireのwebdriverを使用し、オプションとseleniumwire_optionsを設定
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # URLを開く
    driver.get(url)

    # ページが完全に読み込まれるまで待機
    time.sleep(10)  # 必要に応じて調整

    # ページタイトルを取得し、アルファベット表記に変換
    page_title = driver.title.strip().replace(" ", "_")
    page_title_alphabet = convert_to_alphabet(page_title)  # アルファベットに変換

    # ネットワークリクエストをキャプチャし、一番上のリンクだけを取得
    requested_url = None
    for request in driver.requests:
        if request.response and 'm3u8' in request.url:
            requested_url = request.url
            print(f'ビデオリンク取得: {requested_url}')
            break

    # 処理終了時間を記録
    end_time = time.time()
    elapsed_time = end_time - start_time

    # ブラウザを閉じる
    driver.quit()

    # ビデオリンクが見つからなかった場合
    if not requested_url:
        print("m3u8ファイルのURLが見つかりませんでした。")
        return None, None

    # 保存するファイルのパスを指定
    file_path = '/content/drive/MyDrive/Mokkorikomori/erningvideo/video_link.txt'

    # ディレクトリが存在しない場合、作成
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # ビデオリンクをファイルに保存
    with open(file_path, 'w') as f:  # 'w'モードで新しいファイルとして保存
        f.write(requested_url + '\n')
        print(f"ビデオリンクが '{file_path}' に保存されました。")

    # 処理時間を表示
    print(f"ビデオリンク取得処理時間: {elapsed_time:.2f}秒")

    # 日付とアルファベット表記のページタイトル、ビデオリンクを返す
    return page_title_alphabet, requested_url

# ビデオをダウンロードする関数
def download_video(page_title_alphabet, requested_url):
    # 現在の日付を取得
    current_date = datetime.now().strftime('%Y%m%d')

    # 動画ファイル名を日付とアルファベット表記のページタイトルに基づいて設定
    output_file = f"{current_date}_{page_title_alphabet}.mp4"

    # 動画の保存先ディレクトリ
    output_directory = '/content/drive/MyDrive/Mokkorikomori/erningvideo/videos'

    # Create the directory if it doesn't exist
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Change working directory to the output directory
    os.chdir(output_directory)

    # Define the FFmpeg command
    ffmpeg_command = [
        'ffmpeg',
        '-i', requested_url,
        '-c', 'copy',
        output_file
    ]

    # Record start time
    start_time = time.time()

    # Run the FFmpeg command
    try:
        result = subprocess.run(ffmpeg_command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
        end_time = time.time()
        elapsed_time = end_time - start_time
        print("FFmpeg executed successfully!")
        print(f"Output saved as: {output_file} in directory: {output_directory}")
        print(f"Time taken: {elapsed_time:.2f} seconds")
    except subprocess.CalledProcessError as e:
        end_time = time.time()
        elapsed_time = end_time - start_time
        print("Error while executing FFmpeg:", e.stderr)
        print(f"Time taken until error: {elapsed_time:.2f} seconds")

# Whisperで文字起こしを行い、正規化する関数
def transcribe_and_normalize_audio():
    """OpenAI Whisper Basicモデルを使用して音声ファイルを文字起こしし、統合された後に正規化する"""
    # Whisperモデルのロード
    model = whisper.load_model("base")

    # 音声ファイルが保存されているディレクトリ
    audio_directory = '/content/drive/MyDrive/Mokkorikomori/erningvideo/audio_files'

    # スクリプトの保存先ディレクトリ
    script_base_directory = '/content/drive/MyDrive/Mokkorikomori/erningvideo/scripts'
    os.makedirs(script_base_directory, exist_ok=True)

    for root, dirs, files in os.walk(audio_directory):
        if 'wav10min' in root:
            mp4name = os.path.basename(os.path.dirname(root))
            script_directory = os.path.join(script_base_directory, mp4name, 'script10min')
            os.makedirs(script_directory, exist_ok=True)

            combined_script_path = os.path.join(script_base_directory, mp4name, f"{mp4name}.txt")
            combined_script_text = ""

            for filename in sorted(files):
                if filename.endswith('.wav'):
                    wav_path = os.path.join(root, filename)
                    file_start_time = time.time()

                    # Whisperモデルで文字起こし
                    result = model.transcribe(wav_path, language='ja')
                    result_text = result['text']

                    # 個別スクリプトを保存
                    script_filename = f"{os.path.splitext(filename)[0]}.txt"
                    script_path = os.path.join(script_directory, script_filename)

                    with open(script_path, 'w', encoding='utf-8') as f:
                        f.write(result_text)

                    combined_script_text += result_text + "\n"
                    file_end_time = time.time()
                    file_duration = file_end_time - file_start_time

                    print(f"Script saved: {script_path}")
                    print(f"Time taken for {filename}: {file_duration:.2f} seconds")

            cleaned_text = clean_text(combined_script_text)
            formatted_text = format_text(cleaned_text)

            with open(combined_script_path, 'w', encoding='utf-8') as f:
                f.write(formatted_text)

            print(f"Combined script saved and normalized: {combined_script_path}")

# 英訳を行う関数
def translate_script():
    """正規化された日本語のスクリプトを英訳する"""
    script_base_directory = '/content/drive/MyDrive/Mokkorikomori/erningvideo/scripts'
    mp4name = "example"  # 必要に応じてファイル名を指定
    combined_script_path = os.path.join(script_base_directory, mp4name, f"{mp4name}.txt")

    # スクリプトを読み込み
    with open(combined_script_path, 'r', encoding='utf-8') as f:
        formatted_text = f.read()

    # 日本語から英語に翻訳
    translated_script_text = translate_text(formatted_text)

    formatted_translated_text = format_english_text(translated_script_text)

    # 翻訳されたスクリプトを保存
    translated_script_path = os.path.join(script_base_directory, mp4name, f"{mp4name}_translated.txt")
    with open(translated_script_path, 'w', encoding='utf-8') as f:
        f.write(formatted_translated_text)

    print(f"Translated script saved: {translated_script_path}")

# メイン処理
def main():
    print("選択肢：")
    print("1: ビデオリンク取得＞MP4ダウンロード>MP3変換>文字起こし正規表現＞英訳")
    print("2: MP4ダウンロード>MP3変換>文字起こし正規表現＞英訳")
    print("3: MP3変換>文字起こし正規表現＞英訳")
    print("4: 文字起こし正規表現＞英訳")
    print("5: 英訳")
    print("6: ビデオリンク取得")
    print("7: MP4ダウンロード")
    print("8: MP3変換")
    print("9: 文字起こし正規表現")
    print("10: 英訳")

    choice = input("どちらのコードを実行しますか？（1/2/3/4/5/6/7/8/9/10）：")

    if choice == '1':
        page_title, requested_url = extract_video_link()
        if requested_url:
            download_video(page_title, requested_url)
            transcribe_and_normalize_audio()
            translate_script()
    elif choice == '2':
        page_title = input("ページタイトルを入力してください: ")
        requested_url = input("ビデオリンクを入力してください: ")
        download_video(page_title, requested_url)
        transcribe_and_normalize_audio()
        translate_script()
    elif choice == '3':
        transcribe_and_normalize_audio()
        translate_script()
    elif choice == '4':
        transcribe_and_normalize_audio()
    elif choice == '5':
        translate_script()
    elif choice == '6':
        extract_video_link()
    elif choice == '7':
        page_title = input("ページタイトルを入力してください: ")
        requested_url = input("ビデオリンクを入力してください: ")
        download_video(page_title, requested_url)
    elif choice == '8':
        transcribe_and_normalize_audio()
    elif choice == '9':
        transcribe_and_normalize_audio()
    elif choice == '10':
        translate_script()
    else:
        print("無効な選択です。再試行してください。")


if __name__ == "__main__":
    main()
