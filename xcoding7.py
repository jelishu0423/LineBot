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

 
def lambda_handler(event, context):
    @handler.add(MessageEvent, message=ImageMessage)
    def handle_message(event):
        message_content = line_bot_api.get_message_content(event.message.id)

        tempfile_path = os.path.join("/tmp", "tempfile")
        with open(tempfile_path, 'wb') as fd:
            for chunk in message_content.iter_content():
                fd.write(chunk)
        data_samples = []
        with open(tempfile_path, "rb") as imageFile:
            image_str = base64.b64encode(imageFile.read()).decode('utf-8')
            data_samples.append({'image_bytes': {'b64': image_str}})

        # Create payload request
        payload = json.dumps({"instances": data_samples})
        server_endpoint = 'YOUR_SERVER_ENDPOINT'
        # Send prediction request
        r = requests.post(server_endpoint, data=payload)
        probability = json.loads(r.content)['predictions']
        (cat_probability, dog_probability) = tuple(probability[0])
        response_text = "我來分析，這張圖{0}%是貓{1}，{2}%是狗{3}".format(
            round(cat_probability*100, 1), chr(0x1F63A), round(dog_probability*100, 1), chr(0x1F436))

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=response_text))
    try:
        # get X-Line-Signature header value
        signature = event['headers']['X-Line-Signature']
        # get event body
        body = event['body']
        # handle webhook body
        handler.handle(body, signature)
    except InvalidSignatureError:
        return {'statusCode': 400, 'body': 'InvalidSignature'}
    except Exception as e:
        return {'statusCode': 400, 'body': json.dumps(str(e))}
    return {'statusCode': 200, 'body': 'OK'}

#主程式
import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
