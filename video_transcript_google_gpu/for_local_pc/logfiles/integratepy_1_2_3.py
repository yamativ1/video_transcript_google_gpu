import os
import time
from seleniumwire import webdriver  # Selenium Wireのwebdriverを使用
from selenium.webdriver.chrome.service import Service
from datetime import datetime
import subprocess
from moviepy.editor import VideoFileClip

# 証明書検証を無効にするオプション
seleniumwire_options = {
    'verify_ssl': False  # SSL証明書の検証を無効化
}

# ChromeOptionsの設定
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-gpu')

# Chromeのバイナリパスを指定
chrome_options.binary_location = r'C:\Program Files\Google\Chrome\Application\chrome.exe'

# Linux用のChromeDriverパスを指定（Dockerコンテナ内）
service = Service(executable_path=r'C:\Users\tyamada\Documents\chromedriver-win64\chromedriver.exe')


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

    # ページタイトルを取得
    page_title = driver.title.strip().replace(" ", "_")  # タイトルの空白をアンダースコアに変換

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

    # 日付とページタイトル、ビデオリンクを返す
    return page_title, requested_url


def download_video(page_title, requested_url):
    # 現在の日付を取得
    current_date = datetime.now().strftime('%Y%m%d')

    # 動画ファイル名を日付とページタイトルに基づいて設定
    output_file = f"{current_date}_{page_title}.mp4"

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


def extract_audio_from_videos():
    # 処理時間を計測するために開始時間を記録
    start_time = time.time()

    # 動画ディレクトリのパス
    video_directory = r"C:\Users\tyamada\Desktop\erningvideo\videos"

    # 出力ディレクトリ
    output_directory = r"C:\Users\tyamada\Desktop\erningvideo\audio_files"
    os.makedirs(output_directory, exist_ok=True)

    # 指定ディレクトリ内の全ての動画ファイルを処理
    for filename in os.listdir(video_directory):
        if filename.endswith('.mp4'):
            video_path = os.path.join(video_directory, filename)
            
            # 動画ファイルから音声ファイル（MP3）を抽出
            video_clip = VideoFileClip(video_path)
            audio_clip = video_clip.audio
            
            # 音声の長さ（秒）を取得
            audio_duration = audio_clip.duration
            
            # 保存するディレクトリを生成
            mp3_output_dir = os.path.join(output_directory, os.path.splitext(filename)[0])
            os.makedirs(mp3_output_dir, exist_ok=True)
            
            # MP3ファイルを保存
            mp3_output_path = os.path.join(mp3_output_dir, f"{os.path.splitext(filename)[0]}.mp3")
            audio_clip.write_audiofile(mp3_output_path)
            print(f"MP3ファイル保存完了: {mp3_output_path}")
            
            # 10分ごとにWAVファイルを分割して保存
            wav_output_dir = os.path.join(mp3_output_dir, 'wav10min')
            os.makedirs(wav_output_dir, exist_ok=True)
            
            # 分割する時間の長さを指定（10分 = 600秒）
            segment_duration = 600
            num_segments = int(audio_duration // segment_duration) + 1
            
            # 10分ごとに音声をWAVファイルとして分割して保存
            for i in range(num_segments):
                start_time_segment = i * segment_duration
                end_time_segment = min((i + 1) * segment_duration, audio_duration)
                
                # 音声クリップを分割
                sub_audio_clip = audio_clip.subclip(start_time_segment, end_time_segment)
                
                # 分割した音声ファイルをWAV形式で保存
                output_wav_path = os.path.join(wav_output_dir, f"part_{i+1}_{os.path.splitext(filename)[0]}.wav")
                sub_audio_clip.write_audiofile(output_wav_path, codec='pcm_s16le')
                
                print(f"Processed WAV segment {i+1}: {output_wav_path}")
            
            # 音声クリップを解放
            audio_clip.close()

    # 処理終了時間を記録
    end_time = time.time()

    # 処理にかかった時間を計算
    total_time = end_time - start_time

    # 処理時間を表示
    print(f"全ての動画の音声ファイル変換と分割が完了しました。処理時間: {total_time:.2f}秒")


# メイン処理
def main():
    print("選択肢：")
    print("1: 1から最後まで")
    print("2: 2から最後まで")
    print("3: 3から最後まで")
    print("4: 1だけ")
    print("5: 2だけ")
    print("6: 3だけ")

    choice = input("どちらのコードを実行しますか？（1/2/3/4/5/6）：")

    if choice == '1':
        page_title, requested_url = extract_video_link()
        if requested_url:
            download_video(page_title, requested_url)
            extract_audio_from_videos()
    elif choice == '2':
        page_title = input("ページタイトルを入力してください: ")
        requested_url = input("ビデオリンクを入力してください: ")
        download_video(page_title, requested_url)
        extract_audio_from_videos()
    elif choice == '3':
        extract_audio_from_videos()
    elif choice == '4':
        extract_video_link()
    elif choice == '5':
        page_title = input("ページタイトルを入力してください: ")
        requested_url = input("ビデオリンクを入力してください: ")
        download_video(page_title, requested_url)
    elif choice == '6':
        extract_audio_from_videos()
    else:
        print("無効な選択です。再試行してください。")


if __name__ == "__main__":
    main()
