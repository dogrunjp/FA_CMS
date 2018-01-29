import json
import boto3
from boto3.session import Session



ACCESS_KEY_ID = 'AKIAJMZGIEPXX4F3MVNQ'
SECRET_ACCESS_KEY = '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'
BUCKET_NAME = 'pyss'

JSON_KEY = 'test.json'
input_f = 'contents/error.html'
OBJECGT_NAME = 'index.html'

session = Session(aws_access_key_id=ACCESS_KEY_ID,
                  aws_secret_access_key=SECRET_ACCESS_KEY)

s3 = session.resource('s3')
bucket = s3.Bucket(BUCKET_NAME)


def read_file():
    obj = bucket.Object(OBJECGT_NAME)
    # obj = s3.Object(BUCKET_NAME, OBJECGT_NAME) #こちらでも良い
    # get()メソッドで中身を取得する
    res = obj.get()
    body = res['Body'].read()
    print(body.decode('utf-8'))


def put_object():
    put_object_name = 'test_name_list.txt'
    obj = bucket.Object(put_object_name)

    body = 'それはただの気分だ'
    res = obj.put(Body=body.encode('utf-8'),
                  ContentEncoding='utf-8',
                  ContentType='text/plane')

    # このママだとS3コンソールでの「公開」処理（ボタン押すだけ）が必要


def put_json():
    json_name = 'test_test2.json'
    obj = s3.Object(BUCKET_NAME, json_name)
    test_json = {'key': 'value'}
    res = obj.put(Body = json.dumps(test_json))

    print(obj.get()['Body'].read())
    # このママだとS3コンソールでの「公開」処理（ボタン押すだけ）が必要


put_json()
