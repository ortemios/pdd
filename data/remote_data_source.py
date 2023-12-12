import json

import boto3

import config
from data.data_source import DataSource


class RemoteDataSource(DataSource):

    BUCKET_NAME = 'pddrussia'

    def __init__(self):
        session = boto3.session.Session()
        self.s3 = session.client(
            service_name='s3',
            region_name='us-east-1',
            endpoint_url='https://storage.yandexcloud.net',
            aws_access_key_id=config.ACCESS_ID,
            aws_secret_access_key=config.ACCESS_KEY,
        )

    async def write_json(self, path: str, data: dict):
        self.s3.put_object(
            Bucket=self.BUCKET_NAME,
            Key=path,
            Body=json.dumps(data),
            StorageClass='COLD'
        )

    async def read_json(self, path: str) -> dict:
        get_object_response = self.s3.get_object(
            Bucket=self.BUCKET_NAME,
            Key=path,
        )
        body = get_object_response['Body'].read().decode()
        return json.loads(body)

    async def list_dir(self, path: str) -> list[str]:
        res = []
        for item in self.s3.list_objects(Bucket=self.BUCKET_NAME)['Contents']:
            key = item['Key']
            if key.startswith(path):
                name = key[len(path)+1:].split('/')[0]
                if name:
                    res.append(name)
        return res


    # session = boto3.session.Session()
    # s3 = session.client(
    #     service_name='s3',
    #     endpoint_url='https://storage.yandexcloud.net'
    # )
    #
    # # Создать новый бакет
    # s3.create_bucket(Bucket='bucket-name')
    #
    # # Загрузить объекты в бакет
    #
    # ## Из строки
    # s3.put_object(Bucket='bucket-name', Key='object_name', Body='TEST', StorageClass='COLD')
    #
    # ## Из файла
    # s3.upload_file('this_script.py', 'bucket-name', 'py_script.py')
    # s3.upload_file('this_script.py', 'bucket-name', 'script/py_script.py')
    #
    # # Получить список объектов в бакете
    # for key in s3.list_objects(Bucket='bucket-name')['Contents']:
    #     print(key['Key'])
    #
    # # Удалить несколько объектов
    # forDeletion = [{'Key': 'object_name'}, {'Key': 'script/py_script.py'}]
    # response = s3.delete_objects(Bucket='bucket-name', Delete={'Objects': forDeletion})
    #
    # # Получить объект
    # get_object_response = s3.get_object(Bucket='bucket-name', Key='py_script.py')
    # print(get_object_response['Body'].read())