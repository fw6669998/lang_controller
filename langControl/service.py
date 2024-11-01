import json

import re
import langControl.llm as llm
from langControl.IotClient import IotClient


def matchDevice(cmd):
    # 搜索
    devices = IotClient.getDevices()
    deviceNames = str.join(',', devices.keys())
    prompt = f"根据指令判断是对以下设备中哪一个. 设备名称列表:{deviceNames}. 指令:{cmd}. 返回内容为设备名称,不要返回其他内容"
    llmRes = llm.getAnswer(prompt)
    device = devices[llmRes]
    if device is None:
        raise Exception("设备未找到")
    return device


def getThingModelObj(productKey):
    # response = tool.requestGetIot("/api/iotThing/getThingModel?iotId=" + iotId)
    # thingModelJson = response['data']['thingModelJson']
    thingModelJson = IotClient.getThingModel(productKey)
    jsonObj = json.loads(thingModelJson)
    services = jsonObj['services']
    properties = jsonObj['properties']
    # 清理不重要的内容
    newServices = []
    for service in services:
        if service['identifier'] == 'set':
            continue
        # 移除不需要的字段
        removeItems = ['callType', 'createTs', 'custom', 'enableStorage', 'productKey', 'required']
        for item in removeItems:
            if item in service:
                service.pop(item)
        newServices.append(service)
    newProperties = []
    for property in properties:
        removeItems = ['createTs', 'custom', 'customFlag', 'enableStorage', 'productKey', 'required', 'std']
        for item in removeItems:
            if item in property:
                property.pop(item)
        newProperties.append(property)
    newThingModel = {'properties': newProperties, 'services': newServices}
    return newThingModel


def getCmdPrompt(cmd, thingModelObj):
    thingModelStr = json.dumps(thingModelObj, ensure_ascii=False)
    # prompt = "根据指令A和物模型数据B生成指令C,仅返回指令C的JSON数据,不要返回其他内容, 指令A=" + cmd + \
    #          ", 指令C格式={\"identifier\":x,\"arg\":y, \"type\":z}, 如果指令A为动作类指令那么z的取值为invokeService," \
    #          "如果指令A的为设置属性类指令那么z的取值为setProperty,如果指令A是疑问语气或询问类指令那么z的取值为askProperty, 物模型数据B=" + thingModelStr
    prompt = '''
    根据自然语言指令A和物模型数据B生成JSON指令C,仅返回指令C的JSON数据,不要返回其他内容.
指令C格式={"identifier":x,"arg":y, "type":z}.
z的取值为invokeService,setProperty,askProperty,根据指令和匹配到identifier判断

以下是假设数据的生成示例:
物模型数据: {"properties":[{"dataSpecsList":[{"dataType":"BOOL","name":"关","value":0},{"dataType":"BOOL","name":"开","value":1}],"identifier":"front_led","name":"前照灯"}],"services":[{"identifier":"move","inputParams":[{"custom":true,"dataSpecsList":[{"dataType":"ENUM","name":"停止","value":0},{"dataType":"ENUM","name":"前进","value":1}],"dataType":"ENUM","identifier":"direct","name":"方向","paraOrder":0}],"outputParams":[],"productKey":"iy4uZ0wl6MA","required":false,"serviceName":"自由移动"}]}
当指令A为: 小车1前进
返回内容为: {"identifier":"move","arg":{"direct":1},"type":"invokeService"}
当指令A为: 小车1开启前照灯
返回内容为: {"identifier": "front_led","arg": 1,"type": "setProperty"}
当指令A为: 小车1前照灯状态
返回内容为: {"identifier": "front_led","arg": "","type": "askProperty"}

以下是实际数据, 请根据该数据生成结果
物模型数据B: {{thingModelStr}}
指令A: {{cmd}}
返回内容为:
'''
    prompt = prompt.replace('{{thingModelStr}}', thingModelStr).replace('{{cmd}}', cmd)
    return prompt


def parseIotCmd(text):
    # 使用正则匹配获取text中JSON字符串
    # json_pattern = r'\{(?:[^{}]|(?R))*\}'
    if text.startswith('{') and "".endswith('}'):
        return text
    json_pattern = r'\{.*\}'
    matches = re.findall(json_pattern, text, re.DOTALL)
    # 打印所有找到的JSON字符串，如果需要，可以将其转换为Python字典
    for match in matches:
        # print('找到的JSON字符串:', match)
        try:
            jsonObj = json.loads(match)
            # print('转换为Python字典:', json_data)
            return jsonObj
        except json.JSONDecodeError:
            print('内容中没有JSON字符串')
            return {'type': 'other'}
    return None


def getIdentifierText(identifier, thingModelObj):
    services = thingModelObj['services']
    for service in services:
        if service['identifier'] == identifier:
            return service['serviceName']
    properties = thingModelObj['properties']
    for property in properties:
        if property['identifier'] == identifier:
            return property['name']
    return identifier


def getAskValue(identifier, res):
    value = '未获取到'
    try:
        if 'data' in res:
            value = res['data'][identifier]['value']
        # askRes是对象类型
        if isinstance(value, dict):
            value = json.dumps(value, ensure_ascii=False)
    except KeyError:
        return value
    return value


def getValueText(identifier, value, thingModelObj):
    properties = thingModelObj['properties']
    for property in properties:
        if property['identifier'] == identifier and property['dataType'] in ['BOOL', 'ENUM']:
            for item in property['dataSpecsList']:
                if value == item['value'] or value == str(item['value']):
                    return str(value) + '(' + item['name'] + ')'
    return value


def checkCmd(cmdObj, propertyServices, iotId):
    for item in propertyServices:
        if cmdObj['identifier'] == item['identifier']:  # and 'description' in item and item['description'] != '':
            cmd = json.dumps(cmdObj, ensure_ascii=False)
            funDesc = json.dumps(item, ensure_ascii=False)
            properties = IotClient.getProperty(iotId)
            properties2 = []
            for property in properties:
                property2 = {}
                property2['name'] = property.name
                property2['identifier'] = property.identifier
                property2['value'] = property.value
                property2['unit'] = property.unit
                properties2.append(property2)
            propertiesStr = json.dumps(properties2, ensure_ascii=False)
            prompt = f"根据功能描述和设备当前状态值判断判断指令是否能正确执行,如果能返回'检查通过', 否则返回原因,不要返回其他内容, \n+功能描述: {funDesc} \n+设备当前状态: {propertiesStr} \n+指令: {cmd}"
            llmRes = llm.getAnswer(prompt)
            if '检查通过' in llmRes:
                return 'yes'
            else:
                return llmRes
    return "yes"


def invokeIotCmd(iotId, cmdObj, thingModelObj):
    print('执行指令:', cmdObj)
    res = cmdObj
    res['cmdAttention'] = ''
    response = '未执行'
    if cmdObj['type'] == 'invokeService':
        res['typeText'] = '调用服务'
        checkRes = checkCmd(cmdObj, thingModelObj['services'], iotId)
        if checkRes != 'yes':
            res['cmdAttention'] = checkRes
        else:
            response = IotClient.invokeService(iotId, cmdObj['identifier'], json.dumps(cmdObj['arg']))
    elif cmdObj['type'] == 'setProperty':
        params = '{"' + cmdObj['identifier'] + '":' + str(cmdObj['arg']) + '}'
        res['typeText'] = '设置属性'
        checkRes = checkCmd(cmdObj, thingModelObj['properties'], iotId)
        res['arg'] = getValueText(cmdObj['identifier'], res['arg'], thingModelObj)
        if checkRes != 'yes':
            res['cmdAttention'] = checkRes
        else:
            response = IotClient.setProperty(iotId, params)
    elif cmdObj['type'] == 'askProperty':
        res['typeText'] = '询问属性'
        propertys = IotClient.getProperty(iotId)
        value = None
        for item in propertys:
            if item.identifier == cmdObj['identifier']:
                value = item.value
                break
        res['askValue'] = value
        res['askText'] = getValueText(cmdObj['identifier'], value, thingModelObj)
    res['iotExecRes'] = response
    # cmdObj['success'] = response['status'] == 'S'
    return res
