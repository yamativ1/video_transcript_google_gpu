from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time

# ChromeDriverのパスを指定
service = Service(executable_path='C:/Users/tyamada/Documents/chromedriver-win64/chromedriver.exe')

def generate_mp4_url_from_iframe():
    # ChromeOptionsを設定して、ヘッドレスモードを有効化
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')  # ヘッドレスモード
    chrome_options.add_argument('--no-sandbox')  # サンドボックス無効化
    chrome_options.add_argument('--disable-dev-shm-usage')  # /dev/shm 使用を無効化
    chrome_options.add_argument('--disable-gpu')  # GPU無効化

    # Seleniumを使用してページを取得
    driver = webdriver.Chrome(service=service, options=chrome_options)
    url = "https://c-hotline.net/Viewer/Default/4679234679629bb7bc2153936e3a8ceca580"
    driver.get(url)

    # ページが完全に読み込まれるまで待機
    time.sleep(5)

    # すべてのiframeを取得して、そのsrc属性を出力
    iframes = driver.find_elements(By.TAG_NAME, 'iframe')
    print(f"見つかったiframeの数: {len(iframes)}")

    # 2番目のiframeを取得
    if len(iframes) > 1:
        iframe_src = iframes[1].get_attribute('src')
        print(f"iframe 2 のURL: {iframe_src}")

        # ロジックに基づいてMP4のURLを生成
        mp4_url = generate_mp4_url(iframe_src)
        print(f"生成されたMP4 URL: {mp4_url}")
    else:
        print("2番目のiframeが見つかりませんでした。")

    driver.quit()

def generate_mp4_url(iframe_url):
    # "arc/"から次の"/"までの部分を取り出す
    try:
        arc_index = iframe_url.index('arc/')
        next_slash_index = iframe_url.index('/', arc_index + 4)
        portion = iframe_url[arc_index + 4:next_slash_index]
    except ValueError:
        print("URL内に 'arc/' または '/' が見つかりませんでした。")
        return None

    # "rev"以前の部分を取り出し、小文字に変換
    rev_index = portion.find('rev')
    if rev_index != -1:
        portion = portion[:rev_index]  # 'rev'以前の部分を取り出す
    portion = portion.lower()  # 小文字に変換

    # 新しいMP4のURLを生成
    mp4_url = f"{iframe_url}/src/media/{portion}.mp4"
    return mp4_url

# スクリプトの実行
generate_mp4_url_from_iframe()
