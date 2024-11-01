# 加载.env配置文件
from dotenv import load_dotenv
load_dotenv(verbose=True)

import json
from flask import request, Flask, jsonify
from langControl import service, llm

app = Flask(__name__)


@app.route('/')
def hello_world():  # put application's code here
    return "<script>window.location = '/static/index.html';</script>"


@app.route('/cmd', methods=['POST'])
def cmd():
    srcCmd = request.form.get('cmd')
    device = service.matchDevice(srcCmd)
    iotId = device['iot_id']
    thingModelObj = service.getThingModelObj(device['product_key'])
    prompt = service.getCmdPrompt(srcCmd, thingModelObj)
    langModelRes = llm.getAnswer(prompt)
    iotCmd = service.parseIotCmd(langModelRes)
    res = service.invokeIotCmd(iotId, iotCmd, thingModelObj)

    res['identifierText'] = service.getIdentifierText(iotCmd['identifier'], thingModelObj)
    res['deviceName'] = device['device_name'] + '(' + device['nickname'] + ')'
    res['srcCmd'] = srcCmd
    res['prompt'] = prompt
    res['thingModelObj'] = thingModelObj
    res['iotId'] = iotId
    res['langModelRes'] = langModelRes
    if isinstance(res['arg'], dict):
        res['arg'] = json.dumps(res['arg'], ensure_ascii=False)
    print('iotExecRes: ', res['iotExecRes'])
    # 返回json
    return jsonify(res)


if __name__ == '__main__':
    app.run(port=5001, host='0.0.0.0')
