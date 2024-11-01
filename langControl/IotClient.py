# -*- coding: utf-8 -*-
# This file is auto-generated, don't edit it. Thanks.
import os
from typing import List
from alibabacloud_iot20180120.client import Client as Iot20180120Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_iot20180120 import models as iot_20180120_models
from alibabacloud_tea_util import models as util_models

"""
使用AK&SK初始化账号Client
@return: Client
@throws Exception
"""
# 工程代码泄露可能会导致 AccessKey 泄露，并威胁账号下所有资源的安全性。以下代码示例仅供参考。
# 建议使用更安全的 STS 方式，更多鉴权访问方式请参见：https://help.aliyun.com/document_detail/378659.html。
config = open_api_models.Config(
    # 必填，请确保代码运行环境设置了环境变量 ALIBABA_CLOUD_ACCESS_KEY_ID。,
    access_key_id=os.environ['ALIBABA_CLOUD_ACCESS_KEY_ID'],
    # 必填，请确保代码运行环境设置了环境变量 ALIBABA_CLOUD_ACCESS_KEY_SECRET。,
    access_key_secret=os.environ['ALIBABA_CLOUD_ACCESS_KEY_SECRET']
)
# Endpoint 请参考 https://api.aliyun.com/product/Iot
config.endpoint = f'iot.cn-shanghai.aliyuncs.com'
client = Iot20180120Client(config)
iotInstanceId = os.getenv('ALIBABA_CLOUD_IOT_INSTANCE_ID')


class IotClient:
    devices = {}

    @staticmethod
    def getProducts() -> List[str]:
        query_product_list_request = iot_20180120_models.QueryProductListRequest(
            iot_instance_id=iotInstanceId,
            current_page=1,
            page_size=10
        )
        runtime = util_models.RuntimeOptions()
        res = client.query_product_list_with_options(query_product_list_request, runtime)
        productKeys = []
        for item in res.body.data.list.product_info:
            productKeys.append(item.product_key)
        return productKeys

    @staticmethod
    def getProductDevices(productKey):
        query_device_list_request = iot_20180120_models.QueryDeviceRequest(
            iot_instance_id=iotInstanceId,
            product_key=productKey,
            current_page=1,
            page_size=10
        )
        runtime = util_models.RuntimeOptions()
        res = client.query_device_with_options(query_device_list_request, runtime)
        devices = {}
        if res.body.data is not None:
            for item in res.body.data.device_info:  # iy4uj0maGWx 1FZdOaYHCo5FCdAdT0MH  iot-06z00dsogje3o1n 1FZdOaYHCo5FCdAdT0MHiy4u00
                device = {
                    'product_key': productKey,
                    'iot_id': item.iot_id,
                    'device_name': item.device_name,
                    'nickname': item.nickname,
                    'name': item.nickname if item.nickname else item.device_name,
                }
                devices[device['name']] = device
        return devices

    @staticmethod
    def getDevices():
        if IotClient.devices != {}:
            return IotClient.devices
        products = IotClient.getProducts()
        devices = {}
        for productKey in products:
            devices1 = IotClient.getProductDevices(productKey)
            for k, v in devices1.items():
                devices[k] = v
        IotClient.devices = devices
        return devices

    @staticmethod
    def getThingModel(productKey):
        query_thing_model_request = iot_20180120_models.QueryThingModelRequest(
            iot_instance_id=iotInstanceId,
            product_key=productKey
        )
        runtime = util_models.RuntimeOptions()
        res = client.query_thing_model_with_options(query_thing_model_request, runtime)
        return res.body.data.thing_model_json

    @staticmethod
    def invokeService(iotId, service, params):
        request = iot_20180120_models.InvokeThingServiceRequest(
            iot_instance_id=iotInstanceId,
            iot_id=iotId,
            args=params,
            identifier=service
        )
        runtime = util_models.RuntimeOptions()
        res = client.invoke_thing_service_with_options(request, runtime)
        return IotClient.getExecRes(res.body)

    @staticmethod
    def getExecRes(body):
        if body.success:
            return "发送指令成功"
        else:
            resText = "发送指令失败, "
            if hasattr(body, 'error_message') and body.error_message:
                resText = resText + body.error_message
            else:
                resText = resText + body.code
            return resText

    @staticmethod
    def setProperty(iotId, items):
        request = iot_20180120_models.SetDevicePropertyRequest(
            iot_instance_id=iotInstanceId,
            iot_id=iotId,
            items=items
        )
        runtime = util_models.RuntimeOptions()
        res = client.set_device_property_with_options(request, runtime)
        return IotClient.getExecRes(res.body)

    @staticmethod
    def getProperty(iotId):
        request = iot_20180120_models.QueryDevicePropertyStatusRequest(
            iot_instance_id=iotInstanceId,
            iot_id=iotId
        )
        runtime = util_models.RuntimeOptions()
        res = client.query_device_property_status_with_options(request, runtime)
        return res.body.data.list.property_status_info
        # 返回示例 [{'data_type': 'bool', 'identifier': 'completed', 'name': '传送完成', 'time': '1698109830435', 'unit': '', 'value': '1'}]


if __name__ == '__main__':
    res = None
    # res = IotClient.getDevices()
    # res = IotClient.getThingModel('iy4uj0maGWx')
    # res = IotClient.invokeService('1FZdOaYHCo5FCdAdT0MHiy4u00', 'feed_cylinder_act', '{"val":1}')
    # res = IotClient.setProperty('1FZdOaYHCo5FCdAdT0MHiy4u00', '{"transfer_mode":1}')
    res = IotClient.getProperty('1FZdOaYHCo5FCdAdT0MHiy4u00')

    print(res)
