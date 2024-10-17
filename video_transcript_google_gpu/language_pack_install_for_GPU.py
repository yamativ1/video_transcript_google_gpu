import os
os.environ['ARGOS_DEVICE_TYPE'] = 'cuda'
import argostranslate.package
import argostranslate.translate

# 日本語と英語の言語パッケージをダウンロードしてインストール
def install_language_package(from_lang="ja", to_lang="en"):
    # 利用可能なパッケージを取得
    available_packages = argostranslate.package.get_available_packages()

    # 日本語から英語の言語パッケージを検索
    package_to_install = next(
        filter(lambda x: x.from_code == from_lang and x.to_code == to_lang, available_packages),
        None
    )

    if package_to_install is not None:
        # パッケージをダウンロード
        package_path = package_to_install.download()

        # パッケージをインストール
        argostranslate.package.install_from_path(package_path)
        print(f"'{from_lang}' から '{to_lang}' の言語パッケージをインストールしました。")
    else:
        print(f"'{from_lang}' から '{to_lang}' の言語パッケージが見つかりませんでした。")

# 日本語から英語のパッケージをインストール
install_language_package("ja", "en")