import requests
import json

# WEB_HOOK_URLは下準備で発行したURLを設定しください
WEB_HOOK_URL = "https://hooks.slack.com/services/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"

requests.post(WEB_HOOK_URL, data=json.dumps({
    "text" : "送信テスト",
}))