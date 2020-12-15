# -*- coding: utf-8 -*-
import json
import os
from boto3.session import Session

def download_file(file,type):
    session = Session(
        region_name='us-east-2'
    )

    s3 = session.client("s3")
    bucket = file.split("/")[2]
    key = "/".join(file.split("/")[3:])
    name = file.split("/")[-1]
    save_path = os.path.join(image_folder,type,name)
    s3.download_file(bucket, key, save_path)
    print ("<<<download success for : ", file)

def main(train_number,valid_number,label_json,image_folder):
    assert type(train_number) is int
    assert type(valid_number) is int

    annotations = json.load(open(label_json))

    #make train/valid folders
    if not os.path.exists(image_folder):
        os.mkdir(image_folder)

    os.mkdir(os.path.join(image_folder,'train'))
    os.mkdir(os.path.join(image_folder,'val'))

    if (valid_number+train_number)<len(label_json):
        train_ls = list(annotations.keys())[:train_number]
        valid_ls = list(annotations.keys())[train_number:(train_number+valid_number)]

        train_s3_ls = ['s3://lianbao-mask-rcnn/data/' + '/'.join(i.split('/')[3:]) for i in train_ls]
        valid_s3_ls = ['s3://lianbao-mask-rcnn/data/' + '/'.join(i.split('/')[3:]) for i in valid_ls]

        #download files and save to related folders
        for i in train_s3_ls:
            download_file(i, 'train')
        for i in valid_s3_ls:
            download_file(i, 'val')

        #generate train and test labeled data
        train_via_data = {key: value for key, value in annotations.items() if key in train_ls}
        valid_via_data = {key: value for key, value in annotations.items() if key in valid_ls}
        train_json = os.path.join(image_folder,'train','via_region_data.json')
        valid_json = os.path.join(image_folder,'val','via_region_data.json')
        with open(train_json, "w") as myfile:
            json.dump(train_via_data, myfile)
        with open(valid_json, "w") as myfile:
            json.dump(valid_via_data, myfile)

    else:
        print ('number is not valid!')

if __name__ == "__main__":
    train_number = 1
    valid_number = 1
    label_json = '../../data/via_region_data.json'
    image_folder = '../../data'
    main(train_number, valid_number, label_json, image_folder)
