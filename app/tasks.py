import getpass
from datetime import datetime
from sdmetrics.reports.single_table import QualityReport
import pandas as pd
from celery import Celery
from metadata.dataset import Metadata
# from sdv.tabular import CTGAN
from utilities import get_database, writeData, syntheticdataSave
from check_status import simple_send


#ctgan dependency modules


import argparse
import sys

from ctgan.data import read_csv, read_tsv, write_tsv
from ctgan.synthesizer.ctgan import CTGAN_New
from utilities import get_discrete_cols
from conf import PATH
from utilities import _parse_args




app = Celery('tasks', broker='amqp://guest:guest@localhost:5672//')

db = get_database()
collection = db["jobs"]


@app.task
def add(x, y):
    return x + y


@app.task(serializer='json')
def add_data(df, id_var, num_rows, epochs, batch_size, generator_dim,
             log_frequency, embedding_dim, discriminator_dim, emails):
    list_emails = emails.split(',')
    print(df)
    print(list_emails)
    df = pd.DataFrame(eval(df))
    start_time = datetime.now()
    # args = _parse_args()
    discrete_columns = get_discrete_cols(df)
    print(discrete_columns)

    # if args.tsv:
    #     data, discrete_columns = read_tsv(args.data, args.metadata)
    # else:
    #     data, discrete_columns = read_csv(args.data, args.metadata, args.header, args.discrete)

    # if args.load:
    #     model = CTGAN_New.load(args.load)
    # else:
    #     generator_dim = [int(x) for x in generator_dim.split(',')]
    #     discriminator_dim = [int(x) for x in discriminator_dim.split(',')]

    model = CTGAN_New(
        epochs=epochs,
        batch_size=batch_size,
        generator_dim=(generator_dim, generator_dim, generator_dim),
        discriminator_dim=(discriminator_dim, discriminator_dim, discriminator_dim),
        log_frequency=log_frequency,
        embedding_dim=embedding_dim
        )


    model.fit(df, discrete_columns)

    new_df= model.sample(n= num_rows)
    print(id_var)
    syntheticdataSave(dataframe=new_df, file_name=f'syndata_{id_var}')
    print(f'shape of the data: ',{new_df.shape})

    #function calls
    writeData(file_path=f'/home/{getpass.getuser()}/synthetic_data_gen/sythetic_data/syndata_{id_var}.csv', file_name= f'syndata_{id_var}')
    end_time = datetime.now()
    report = QualityReport()
    # get table metadata
    metadata = Metadata()
    metadata.add_table(
        name='data',
        data=df,
    )
    metadata = metadata.get_table_meta('data')
    report.generate(df, new_df, metadata=metadata)
    overall_quality_score = report.get_score()
    column_wise_score = report.get_properties()["Score"].tolist()[0]
    pairwise_score = report.get_properties()["Score"].tolist()[1]

    # send here the email itself
    simple_send(list_emails, epochs, num_rows, generator_dim, log_frequency, embedding_dim, discriminator_dim,
                batch_size, id_var, "Done", start_time, end_time, overall_quality_score, column_wise_score,
                pairwise_score,f'/home/{getpass.getuser()}/synthetic_data_gen/sythetic_data/syndata_{id_var}')

    # put the entry in mongodb
    collection.find_one_and_update({"_id": id_var},
                                   {"$set": {"status": "done"}})

    return {"status": True}
