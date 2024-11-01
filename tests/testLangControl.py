from langControl.service import *


def testGetClearRes():
    # text = """这是一些文本，它包含了一个JSON对象：{"name": "John", "age": 30, "city": "New York"}还有一些其他的文本。"""
    # res = getClearRes(text)
    # print(res)
    text = 'asda{"identifier": "agv_auto", "arg": {"agv_route": 1, "agv_parting": 2, "agv_avoidance": 0, "agv_start": 1}, "type": "invokeService"}sdsds'
    res = parseIotCmd(text)
    print(res)


def testRun(srcCmd):
    iotId = testSearch(srcCmd)
    thingModelInfo = getThingModelObj(iotId)
    prompt = getCmdPrompt(srcCmd, thingModelInfo)
    langModelRes = askLangModel(prompt)
    iotCmd = parseIotCmd(langModelRes)
    invokeRes = invokeIotCmd(iotId, iotCmd)
    deviceInfo = getDeviceInfo(iotId)
    res = {
        'srcCmd': srcCmd,
        'deviceNickName': deviceInfo['nickname'],
        'identifier': iotCmd['identifier'],
        'arg': iotCmd,
        'prompt': prompt,
        'iotExecRes': invokeRes,
        'thingModelObj': thingModelInfo,
        'iotId': iotId,
    }

    # res = iotCmd
    # print('cmd: ', cmd)
    # print('iotId: ', iotId)
    # print('prompt: ', prompt)
    # print('invokeRes: ', invokeRes)
    print(res)
    return invokeRes


def testGetDeviceInfo():
    iotId = testSearch("小车")
    # deviceInfo = getDeviceInfo('H58oQIREH0MpQhFaItH0TAlnq4')
    deviceInfo = getDeviceInfo(iotId)
    print(deviceInfo)


# testGetDeviceInfo()

# testGetClearRes()
# testRun("小车去2点")
# runSaveDeviceVector()  # 保存设备向量
