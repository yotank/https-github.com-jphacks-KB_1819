import sys

import os
from flask import Flask, request, abort, jsonify, Response
import json

import urllib.parse
from OpenSSL import crypto
import base64
import requests

app = Flask(__name__)


@app.route('/', methods=['POST'])
def callback():
    #print(request.get_data())

    #if(validate_request(request.headers, request.get_data()) == False):
    #    abort(400)

    req = CekApi(json.loads(request.get_data(as_text=True)))

    body = request.get_data(as_text=True)
    event = json.loads(body)
    print(event)

    response = json.loads('{ \
        "version": "0.1.0", \
        "sessionAttributes": {}, \
        "response": { \
            "outputSpeech": { \
                "type": "SimpleSpeech", \
                "values": { \
                    "type": "PlainText", \
                    "lang": "ja", \
                    "value": "ここに返答" \
                } \
            }, \
            "reprompt": { \
                "outputSpeech": { \
                    "type": "SimpleSpeech", \
                    "values": { \
                        "type": "PlainText", \
                        "lang": "ja", \
                        "value": "聞き取れませんでした。もう一度お願いします。" \
                    } \
                } \
            }, \
            "card": {}, \
            "directives": [], \
            "shouldEndSession": false \
            } \
        }')





    if event['request']['type'] == 'LaunchRequest':
        response['response']['outputSpeech']['values']['value'] = '食材管理君が起動されました。話しかけて下さい。'
    elif event['request']['type'] == 'IntentRequest':
        print(event['request']['intent']['name'])
        if event['request']['intent']['name'] == 'HelloIntent':
            response['response']['outputSpeech']['values']['value'] = 'ご挨拶して頂きありがとうございます。'
            response['sessionAttributes'] = {'lastIntent' : 'RegisterIntent'}

        elif event['request']['intent']['name'] == 'QuestionIntent':
            response['response']['outputSpeech']['values']['value'] = '好きな果物は何ですか？'

        elif event['request']['intent']['name'] == 'AnswerIntent':
            answer = event['request']['intent']['slots']['fruits']['value']
            response['response']['outputSpeech']['values']['value'] = '%sがお好きなんですね。素敵です。' % answer

        elif event['request']['intent']['name'] == 'AddMaterialWithoutN':
            if event['session']['sessionAttributes'] != null:
                amount = event['session']['sessionAttributes']['amount']
                material = event['request']['intent']['slots']['material'] ['value']
                response['response']['outputSpeech']['values']['value'] = '何個追加materialn個追加'
            else
                response['response']['outputSpeech']['values']['value'] = '何個追加しますか'
                response['sessionAttributes'] = {'material' : event['request']['intent']['slots']['material'] ['value']}

        elif event['request']['intent']['name'] == 'AddNWithoutMaterial':
            response['response']['outputSpeech']['values']['value'] = '何を追加しますか'
            response['sessionAttributes'] = {'amount' : event['request']['intent']['slots']['amount'] ['value']}

        elif event['request']['intent']['name'] == 'Clova.GuideIntent':
            response['response']['outputSpeech']['values']['value'] = '挨拶に返事ができます。質問して、と話しかけると質問を出します。スキルを終了したい時は、キャンセル、と言って下さい。'

        elif event['request']['intent']['name'] == 'Clova.CancelIntent':
            response['response']['outputSpeech']['values']['value'] = 'ご利用ありがとうございました。'
            response['response']['shouldEndSession'] = True

        elif event['request']['intent']['name'] == 'Clova.YesIntent':
            response['response']['outputSpeech']['values']['value'] = '承認のインテントだよ'

        elif event['request']['intent']['name'] == 'Clova.NoIntent':
            response['response']['outputSpeech']['values']['value'] = '否定のインテントです。'



        elif event['request']['intent']['name'] == 'AddMaterial':
            amount = event['request']['intent']['slots']['amount'] ['value']
            material = event['request']['intent']['slots']['material'] ['value']


            sessionAttributes= event['session']['sessionAttributes']
            if material in sessionAttributes:
                kariamount = amount
                sessionAttributes[material] =int(sessionAttributes[material])+int(amount)
                sessionAttributes[material] = str(sessionAttributes[material])
                response['response']['outputSpeech']['values']['value'] = material+'を'+kariamount+'個追加し'+sessionAttributes[material]+'個になりました。'
            else:
                sessionAttributes[material] =amount
                response['response']['outputSpeech']['values']['value'] = material+'を'+amount+'個追加しました。'


            response['sessionAttributes'] ={material:amount}
        elif event['request']['intent']['name'] == 'AskRecipe':
            response['response']['outputSpeech']['values']['value'] = '今ある食材から考えるにカオマンガイがオススメです。'













    return jsonify(response)

def validate_request(headers, body_raw):

    # validate cert url
    cert_url = headers.get('SignatureCEKCertChainUrl')
    if cert_url is None:
        return False
    parsed_url = urllib.parse.urlparse(cert_url)
    cert_validation_result = False
    if parsed_url.scheme == 'https':
        if parsed_url.hostname == "clova-cek-requests.line.me":
            cert_validation_result = True
    if cert_validation_result == False:
        return False

    # validate signature
    if headers.get('SignatureCEK') is None or headers.get('SignatureCEKCertChainUrl') is None:
        return False

    cert_str = requests.get(cert_url)
    certificate = crypto.load_certificate(crypto.FILETYPE_PEM, str(cert_str.text))
    if certificate.has_expired() is True:
        return False
    if certificate.get_subject().CN != "clova-cek-requests.line.me":
        return False
    decoded_signature = base64.b64decode(headers.get('SignatureCEK'))

    signature_validation_result = False

    if crypto.verify(certificate, decoded_signature, body_raw, 'sha1') is None:
        signature_validation_result = True

    if signature_validation_result == False:
        return False

    return True

class CekApi():
    def __init__(self, object):
        print()

if __name__ == '__main__':
    app.debug = True;
    app.run(host='0.0.0.0')
