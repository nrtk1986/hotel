import requests
import json
import os

# WEB_HOOK_URLは下準備で発行したURLを設定しください
WEB_HOOK_URL = os.environ["SLACK_URL"]

requests.post(WEB_HOOK_URL, data=json.dumps({
    "text" : "送信テスト",
}))git