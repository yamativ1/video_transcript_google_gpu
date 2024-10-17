import os
import time
from seleniumwire import webdriver  # Selenium Wireのwebdriverを使用
from selenium.webdriver.chrome.service import Service
from datetime import datetime
import subprocess
from moviepy.editor import VideoFileClip
import jaconv  # 日本語からアルファベット表記に変換
import json
import wave
import vosk
import soundfile as sf
import io
import numpy as np
import re


# スペースで分割されている単語を整理する関数
def clean_text(text):
    # 空白を適切に削除して単語をまとめる
    text = re.sub(r'(\w+)\s(\w+)', r'\1\2', text)  # ひらがなと漢字が分かれている箇所を修正
    text = re.sub(r'(\d+)\s(\w+)', r'\1\2', text)  # 数字と単位の間のスペースを修正
    text = re.sub(r'\s+', ' ', text)  # 不要な複数の空白を1つにする
    text = re.sub(r'(?<=\d)(\s)(?=\d)', '', text)  # 数字同士のスペースを削除
    return text

# 句読点や改行を追加して自然な文章にする関数
def format_text(text):
    text = re.sub(r'(ます|です)(\s)', r'\1。\n', text)  # 文末に句点を追加
    text = re.sub(r'(が|で|と|を|に|へ)(\s)', r'\1、', text)  # 文の区切りに読点を追加
    return text

# 日本語をアルファベット表記に変換する関数
def convert_to_alphabet(text):
    return jaconv.kana2alphabet(text)

def extract_video_link():
    # URLをファイルから読み込む
    with open(r'C:\Users\tyamada\Desktop\project\target.txt', 'r') as file:
        url = file.read().strip()

    # 読み込んだURLを表示
    print(f"読み込んだURL: {url}")

    # 処理開始時間を記録
    start_time = time.time()

    # Selenium Wireのwebdriverを使用し、オプションとseleniumwire_optionsを設定
    driver = webdriver.Chrome(service=service, options=chrome_options, seleniumwire_options=seleniumwire_options)

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
    file_path = r'C:\Users\tyamada\Desktop\erningvideo\video_link.txt'

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


def download_video(page_title_alphabet, requested_url):
    # 現在の日付を取得
    current_date = datetime.now().strftime('%Y%m%d')

    # 動画ファイル名を日付とアルファベット表記のページタイトルに基づいて設定
    output_file = f"{current_date}_{page_title_alphabet}.mp4"

    # Specify the output directory
    output_directory = r'C:\Users\tyamada\Desktop\erningvideo\videos'

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
        # エンコーディングを指定してサブプロセスの出力を処理
        result = subprocess.run(ffmpeg_command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
        # Record end time and calculate elapsed time
        end_time = time.time()
        elapsed_time = end_time - start_time
        print("FFmpeg executed successfully!")
        print(f"Output saved as: {output_file} in directory: {output_directory}")
        print(f"Time taken: {elapsed_time:.2f} seconds")
    except subprocess.CalledProcessError as e:
        # Handle FFmpeg errors
        end_time = time.time()
        elapsed_time = end_time - start_time
        print("Error while executing FFmpeg:", e.stderr)
        print(f"Time taken until error: {elapsed_time:.2f} seconds")


def transcribe_and_normalize_audio():
    """Voskを使用して音声ファイルを文字起こしし、統合された後に正規化する"""
    model_path = r"C:\Users\tyamada\Documents\vosk-model-ja-0.22"
    model = vosk.Model(model_path)

    # 音声ファイルが保存されているディレクトリ (10分ごとに分割されたWAVファイル)
    audio_directory = r"C:\Users\tyamada\Desktop\erningvideo\audio_files"

    # スクリプトの保存先ディレクトリ
    script_base_directory = r"C:\Users\tyamada\Desktop\erningvideo\scripts"
    os.makedirs(script_base_directory, exist_ok=True)

    # 指定ディレクトリ内の全てのWAVファイルを処理
    for root, dirs, files in os.walk(audio_directory):
        if 'wav10min' in root:
            mp4name = os.path.basename(os.path.dirname(root))  # mp4ファイル名に相当するディレクトリ名を取得
            script_directory = os.path.join(script_base_directory, mp4name, 'script10min')
            os.makedirs(script_directory, exist_ok=True)

            combined_script_path = os.path.join(script_base_directory, mp4name, f"{mp4name}.txt")
            combined_script_text = ""  # 統合スクリプト用の変数

            for filename in sorted(files):  # ファイルをソートして順番通りに処理
                if filename.endswith('.wav'):
                    wav_path = os.path.join(root, filename)
                    file_start_time = time.time()

                    data, samplerate = sf.read(wav_path)

                    # ステレオ（2チャンネル）の場合はモノラルに変換（平均化）
                    if len(data.shape) > 1 and data.shape[1] == 2:
                        data = np.mean(data, axis=1)

                    wav_io = io.BytesIO()
                    with sf.SoundFile(wav_io, mode='w', samplerate=samplerate, channels=1, subtype='PCM_16', format='WAV') as wav_file:
                        wav_file.write(data)

                    wav_io.seek(0)
                    wf = wave.open(wav_io, "rb")

                    rec = vosk.KaldiRecognizer(model, wf.getframerate())
                    result_text = ""

                    while True:
                        data = wf.readframes(4000)
                        if len(data) == 0:
                            break
                        if rec.AcceptWaveform(data):
                            result = rec.Result()
                            result_json = json.loads(result)
                            result_text += result_json.get('text', '') + "\n"
                        else:
                            partial_result = rec.PartialResult()

                    final_result = rec.FinalResult()
                    result_json = json.loads(final_result)
                    result_text += result_json.get('text', '')

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

            # 最終的に統合されたスクリプトを正規化して保存
            cleaned_text = clean_text(combined_script_text)  # 空白や分割された単語を修正
            formatted_text = format_text(cleaned_text)  # 句読点を追加して自然な文章にする

            with open(combined_script_path, 'w', encoding='utf-8') as f:
                f.write(formatted_text)

            print(f"Combined script saved and normalized: {combined_script_path}")



# メイン処理
def main():
    print("選択肢：")
    print("1: 1から最後まで")
    print("2: 2から最後まで")
    print("3: 3から最後まで")
    print("4: 4から最後まで")
    print("5: 1だけ")
    print("6: 2だけ")
    print("7: 3だけ")
    print("8: 4だけ")

    choice = input("どちらのコードを実行しますか？（1/2/3/4/5/6/7/8）：")

    if choice == '1':
        page_title, requested_url = extract_video_link()
        if requested_url:
            download_video(page_title, requested_url)
            transcribe_and_normalize_audio()
    elif choice == '2':
        page_title = input("ページタイトルを入力してください: ")
        requested_url = input("ビデオリンクを入力してください: ")
        download_video(page_title, requested_url)
        transcribe_and_normalize_audio()
    elif choice == '3':
        transcribe_and_normalize_audio()
    elif choice == '4':
        # その他の処理（必要に応じて追加可能）
        pass
    elif choice == '5':
        extract_video_link()
    elif choice == '6':
        page_title = input("ページタイトルを入力してください: ")
        requested_url = input("ビデオリンクを入力してください: ")
        download_video(page_title, requested_url)
    elif choice == '7':
        # その他の処理（必要に応じて追加可能）
        pass
    elif choice == '8':
        # その他の処理（必要に応じて追加可能）
        pass
    else:
        print("無効な選択です。再試行してください。")


if __name__ == "__main__":
    main()
