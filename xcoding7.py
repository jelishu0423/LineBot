#載入LineBot所需要的套件
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

app = Flask(__name__)

# 必須放上自己的Channel Access Token
line_bot_api = LineBotApi('cVuxUh37rdpZfzeIxlzBacx+9nDM/eej2DOry4cVwJDGWF0tkWrQhTKgLnxS5iDzLNybhSrXf/d4iloPvHANce0/akvAUAad1h7BUcIKGHVigu4pvRIWgjD/BwfymT15PwjelfRpr+QJWTpXSkBOfgdB04t89/1O/w1cDnyilFU=')

# 必須放上自己的Channel Secret
handler = WebhookHandler('460f3260ada98363f7b7959b227ec32f')


# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

 
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

 
#訊息傳遞區塊
##### 基本上程式編輯都在這個function #####
@handler.add(MessageEvent, message=ImageMessage)
def handle_message(event):
    # 請api用get_message_content依照訊息id將圖片要回
    message_content = line_bot_api.get_message_content(event.message.id)
    
    from PIL import Image
    from torchvision.transforms import ToTensor
    #ckpt = "0_5442.ckpt"
    #img_path = 'example/70_carlos.bmp'
    #model = LitBTTR.load_from_checkpoint(ckpt)
    img = Image.open(message_content)
    
    # 請api回覆已經上傳
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text='Image has Upload'+ ' ' + event.message.id + '\n' + str(type(img))))


#主程式
import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
