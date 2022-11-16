from pymongo import MongoClient
# from sdv.tabular import CTGAN
from ctgan.synthesizer.ctgan import CTGAN_New
import os
import getpass
from io import StringIO
from conf import CONNECTION_STRING, STORAGE_ACCOUNT_KEY,STORAGE_ACCOUNT_NAME,CONTAINER_NAME, BLOB_NAME



#pyspark modules

import pandas as pd
import numpy as np
import argparse
import pyspark
from pyspark.sql import SparkSession



from azure.storage.blob import BlobServiceClient
from azure.storage.blob import ContainerClient




def writeData(file_path: str, file_name: str):
    storage_account_key= STORAGE_ACCOUNT_KEY
    storage_account_name= STORAGE_ACCOUNT_NAME
    connection_string= CONNECTION_STRING
    container_name = CONTAINER_NAME
    blob_name= BLOB_NAME

    blob_service_client= BlobServiceClient.from_connection_string(connection_string)
    blob_client= blob_service_client.get_blob_client(container= container_name, blob= f'{file_name}.csv')
    

    with open(file_path,"rb") as data:
        blob_client.upload_blob(data)
    print(f'Uploaded {file_name}.') 






def get_database():
    """
    Create mongo client and get the database
    Return
    ------
    db: database
    """
    client = MongoClient('127.0.0.1', 27017)
    return client['jobs_monitor']


def get_data(df, collection, id_var, num_rows, epochs, batch_size, generator_dim,
             log_frequency, embedding_dim, discriminator_dim):
    model = CTGAN(
        epochs=epochs,
        batch_size=batch_size,
        generator_dim=(generator_dim, generator_dim, generator_dim),
        discriminator_dim=(discriminator_dim, discriminator_dim, discriminator_dim),
        log_frequency=log_frequency,
        embedding_dim=embedding_dim
    )
    model.fit(df)
    new_df = model.sample(num_rows=num_rows)
    syntheticdataSave(new_df, file_name=f"syndata_{id_var}")
    # put the entry in mongodb
    collection.find_one_and_update({"_id": id_var},
                                   {"$set": {"status": "done"}})
    return new_df


def write_data(df):
    for i in range(1000000000):
        print(i)
    df.to_csv("dump_data.csv", index=False)


def syntheticdataSave(dataframe, file_name):
    parent_dir = f'/home/{getpass.getuser()}/synthetic_data_gen'
    directory = "sythetic_data"
    path = os.path.join(parent_dir, directory)
    if not os.path.exists(path):
        os.makedirs(path)
        print("Directory '%s' created successfully" % directory)
    else:
        print("Directory '%s' already created" % directory)
    if not os.path.exists(f'{path}/{file_name}_synth.csv'):
        dataframe.to_csv(f'{path}/{file_name}_synth.csv')
    else:
        print("The file '%s' already created" % f'{file_name}_synth.csv')



def get_spark_session() -> pyspark.sql.SparkSession: 
    spark = SparkSession.builder.appName("Spark InputHDFSval").getOrCreate()
    spark.conf.set('fs.azure.sas.ntcontainer.ntsparkstorage.blob.core.windows.net',"?sv=2020-08-04&ss=b&srt=sco&sp=rwdlacix&se=2023-03-02T01:34:27Z&st=2022-03-01T17:34:27Z&spr=https&sig=5GkkpyRpJcSb9vGplHURs%2Fkw%2B4uapJahiz5mhqFK1KQ%3D")
    spark.conf.set("fs.azure", "org.apache.hadoop.fs.azure.NativeAzureFileSystem")
    spark.conf.set("fs.wasbs.impl","org.apache.hadoop.fs.azure.NativeAzureFileSystem")
    return spark



def read_from_azure(input_path):

    # spark=get_spark_session()

    connection_string= CONNECTION_STRING
    container_name = CONTAINER_NAME
    blob_name= input_path
    container_client= ContainerClient.from_connection_string(conn_str=connection_string, container_name=container_name)
    downloaded_blob = container_client.download_blob(BLOB_NAME)
    df_input = pd.read_csv(StringIO(downloaded_blob.content_as_text()))

    # df_input = spark.read.options(delimiter=",", header=True).options(inferSchema=True).csv(input_path)
    # df_input= pd.read_csv(input_path)
    # df_input=col_rename(df_input)
    # df_nai_output = spark.read.options(delimiter=",", header=True).options(inferSchema=True).csv(output_path)
    return df_input




def get_discrete_cols(df):
    # if args.discrete!= None:
    #     # df= pd.read_csv(path)
    cate_feat = df.select_dtypes(include=[np.object])
    nominal_list = cate_feat.columns.tolist()
    return nominal_list




def _parse_args():
    parser = argparse.ArgumentParser(description='CTGAN Command Line Interface')
    parser.add_argument('-e', '--epochs', default=1, type=int,
                        help='Number of training epochs')
    parser.add_argument('-t', '--tsv', action='store_true',
                        help='Load data in TSV format instead of CSV')
    parser.add_argument('--no-header', dest='header', action='store_false',
                        help='The CSV file has no header. Discrete columns will be indices.')

    parser.add_argument('-m', '--metadata', help='Path to the metadata')
    parser.add_argument('-d', '--discrete',
                        help='Comma separated list of discrete columns without whitespaces.', default=None)
    parser.add_argument('-n', '--num-samples', type=int,
                        help='Number of rows to sample. Defaults to the training data size')

    parser.add_argument('--generator_lr', type=float, default=2e-4,
                        help='Learning rate for the generator.')
    parser.add_argument('--discriminator_lr', type=float, default=2e-4,
                        help='Learning rate for the discriminator.')

    parser.add_argument('--generator_decay', type=float, default=1e-6,
                        help='Weight decay for the generator.')
    parser.add_argument('--discriminator_decay', type=float, default=0,
                        help='Weight decay for the discriminator.')

    parser.add_argument('--embedding_dim', type=int, default=128,
                        help='Dimension of input z to the generator.')
    parser.add_argument('--generator_dim', type=str, default='256,256,256',
                        help='Dimension of each generator layer. '
                        'Comma separated integers with no whitespaces.')
    parser.add_argument('--discriminator_dim', type=str, default='256,256,256',
                        help='Dimension of each discriminator layer. '
                        'Comma separated integers with no whitespaces.')

    parser.add_argument('--batch_size', type=int, default=500,
                        help='Batch size. Must be an even number.')
    parser.add_argument('--save', default=None, type=str,
                        help='A filename to save the trained synthesizer.')
    parser.add_argument('--load', default=None, type=str,
                        help='A filename to load a trained synthesizer.')

    parser.add_argument('--sample_condition_column', default=None, type=str,
                        help='Select a discrete column name.')
    parser.add_argument('--sample_condition_column_value', default=None, type=str,
                        help='Specify the value of the selected discrete column.')

    # parser.add_argument('--data', help='Path to training data', default='/home/ntlpt-42/synthetic_data_gen/real_data/bank.csv')
    # parser.add_argument('--output', help='Path of the output file', default='/home/ntlpt-42/synthetic_data_gen/real_data')

    return parser.parse_args()



def syntheticdataSave(dataframe: int, file_name: str):

    parent_dir= f'/home/{getpass.getuser()}/synthetic_data_gen'

    directory = "sythetic_data"

    path = os.path.join(parent_dir, directory)

    if not os.path.exists(path):

        os.makedirs(path)

        print("Directory '%s' created successfully" % directory)

    else:

        print("Directory '%s' already created" % directory)



    if not os.path.exists(f'{path}/{file_name}.csv'):

        dataframe.to_csv(f'{path}/{file_name}.csv')

    else:

        print("The file '%s' already created" % f'{file_name}.csv')





#https://ntsp arkstorage.blob.core.windows.net/ntcontainer/AllDateConverts.csv

if __name__=="__main__":
    path= 'wasbs://ntcontainer@ntsparkstorage.blob.core.windows.net/AllDateConverts.csv'
    df= read_from_azure(path)
    df.show()
    print(df.count())
    id_var='63689ccd60d2ae229f9e48b6'
    writeData(file_path=f'/home/{getpass.getuser()}/synthetic_data_gen/sythetic_data/syndata_{id_var}', file_name= f'syndata_{id_var}')

#wasbs://ntcontainer@ntsparkstorage.blob.core.windows.net/AllDateConverts.csv


