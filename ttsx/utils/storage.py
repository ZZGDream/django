# 自定义存储类，将内容存储到fastdfs
from django.core.files.storage import Storage
from fdfs_client.client import Fdfs_client
from django.conf import settings


class FdfsStorage(Storage):
    # 重写storage类的save方法
    def save(self, name, content, max_length=None):
        buffer = content.read()
        # 根据配置文件创建的客户端的实例对象
        client = Fdfs_client(settings.FDFS_CLIENT)
        client = Fdfs_client()
        # 上传文件数据
        try:
            result = client.upload_by_buffer(buffer)
        except:
            raise
            # result = client.upload_by_file('01.jpg')
        # {'Uploaded size': '13.00KB', 'Storage IP': '192.168.254.3', '
        # Group name': 'group1', 'Status': 'Upload successed.‘}
        # print(result)
        if result.get('Status') == 'Upload successed.':
            return result.get('Remote file_id')
        else:
            raise Exception('上传失败')

    # name为文件的名称
    def url(self, name):
        # return 'http//:127.0.0.1:8888' + name
        return settings.FDFS_SEVER + name
