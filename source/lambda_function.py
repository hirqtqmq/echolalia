"""
作成者：

"""
# ライブラリのインポート
import os
import sys
from linebot import (LineBotApi, WebhookHandler)
from linebot.models import (MessageEvent, TextMessage, TextSendMessage,)
from linebot.exceptions import (LineBotApiError, InvalidSignatureError)
import logging
import json
import re

#ロギング関数のデフォルトレベルの設定．ソフトウェア中の機能が実行できないときに実行される関数．getloggerの引数がないのでプログラム全体で不具合が起きたときに警告
logger = logging.getLogger()
logger.setLevel(logging.ERROR)

# チャネルシークレット，アクセストークンの取得．LINE Developersから持ってきてlambdaの環境変数に指定済み
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
if channel_secret is None:
    logger.error('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    logger.error('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

# 取得した変数をライブラリline_bot_sdkから持ってきた関数に渡す
line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

# AWSのlambdaは実行してくれる始めにlambda_handlerと定義された関数を実行するので用意する
def lambda_handler(event, context):
    #print(event) # LINEから送られてくる情報をログで確認する用
    signature = event["headers"]["X-Line-Signature"] # LINEから送られてきた情報であることを確認するリクエストキー
    body = event["body"]
    ok_json = {"isBase64Encoded": False,"statusCode": 200,"headers": {},"body": ""} # 関数正常実行時の返り値
    error_json = {"isBase64Encoded": False,"statusCode": 403,"headers": {},"body": "Error"} # 関数実行時にエラーが発生した時の返り値

    @handler.add(MessageEvent, message=TextMessage) #テキストメッセージのメッセージイベントが送られて来た時
    def message(line_event):
        text = line_event.message.text  # 送られてきた内容をtextに格納
        m1 = re.match(r'フレンド|ふれんど|friend|フレ|ふれ', text, re.IGNORECASE)
        if (m1 == None):
            reply = '指定された形式で入力してください\nオンライン状況確認 : フレンド　フレ etc...'
            line_bot_api.reply_message(line_event.reply_token, TextSendMessage(text=reply)) #textで指定されたメッセージを格納して返信

        line_bot_api.reply_message(line_event.reply_token, TextSendMessage(text='フレンドリスト'))
    try:
        handler.handle(body, signature) # 署名を検証して問題なければwebhookを行う．問題あればエラーメッセージを返して終了．
    except LineBotApiError as e:
        logger.error("Got exception from LINE Messaging API: %s\n" % e.message)
        for m in e.error.details:
            logger.error("  %s: %s" % (m.property, m.message))
        return error_json
    except InvalidSignatureError:
        return error_json

    return ok_json