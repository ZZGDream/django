#python连接服务器的启动
from fdfs_client.client import Fdfs_client
client = Fdfs_client()
result = client.upload_by_file('01.jpg')
print(result)