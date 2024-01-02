import json

import boto3

import config
from data.file.file_data_source import FileDataSource


class RemoteFileDataSource(FileDataSource):

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
        items = self.s3.list_objects(
            Bucket=self.BUCKET_NAME,
            Prefix=path,
        )['Contents']
        for item in items:
            key = item['Key']
            if key.startswith(path):
                name = key[len(path)+1:].split('/')[0]
                if name:
                    res.append(name)
        return res

    async def generate_link(self, path: str) -> str:
        response = self.s3.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': self.BUCKET_NAME,
                'Key': path
            },
            ExpiresIn=3600
        )
        return response
