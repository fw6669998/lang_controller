# -*- coding: utf-8 -*-
# This file is auto-generated, don't edit it. Thanks.
import os
import sys

from typing import List

from alibabacloud_iot20180120.client import Client as Iot20180120Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_iot20180120 import models as iot_20180120_models
from alibabacloud_tea_util import models as util_models
from alibabacloud_tea_util.client import Client as UtilClient
# 加载.env配置文件
from dotenv import load_dotenv

load_dotenv(verbose=True)


class IotClient:
    client = None
    iotInstanceId = os.getenv('ALIBABA_CLOUD_IOT_INSTANCE_ID')

    def __init__(self):
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
        self.client = Iot20180120Client(config)
        pass

    def getProducts(self) -> List[str]:
        query_product_list_request = iot_20180120_models.QueryProductListRequest(
            iot_instance_id=self.iotInstanceId,
            current_page=1,
            page_size=10
        )
        runtime = util_models.RuntimeOptions()
        res = self.client.query_product_list_with_options(query_product_list_request, runtime)
        productKeys = []
        for item in res.body.data.list.product_info:
            productKeys.append(item.product_key)
        return productKeys

    def getProductDevices(self, productKey):
        query_device_list_request = iot_20180120_models.QueryDeviceRequest(
            iot_instance_id=self.iotInstanceId,
            product_key=productKey,
            current_page=1,
            page_size=10
        )
        runtime = util_models.RuntimeOptions()
        res = self.client.query_device_with_options(query_device_list_request, runtime)
        devices = {}
        if res.body.data is not None:
            for item in res.body.data.device_info:  # iy4uj0maGWx 1FZdOaYHCo5FCdAdT0MH  iot-06z00dsogje3o1n
                device = {
                    'product_key': productKey,
                    'iot_id': item.iot_id,
                    'name': item.nickname if item.nickname else item.device_name
                }
                devices[device['name']] = device
        return devices

    def getDevices(self):
        products = self.getProducts()
        devices = {}
        for productKey in products:
            devices1 = self.getProductDevices(productKey)
            for k, v in devices1.items():
                devices[k] = v
        return devices


if __name__ == '__main__':
    iotClient = IotClient()
    devices = iotClient.getDevices()
    print(devices)
