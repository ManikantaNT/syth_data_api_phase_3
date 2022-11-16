# Synthetic data generation

## Algorithm used: CTGAN

### Implementation: Message Queues

1) RabbitMQ
2) Celery
3) Flower
4) FastApi

Requirements:
conda env create -f env.yml


RunCommands:
#### celery -A tasks worker --loglevel=INFO --concurrency=2
#### celery -A tasks flower --port=5559
#### uvicorn main:app --port 8999 --reload


#http://localhost:5559/task/0793b5b7-f94b-46a8-b584-f1f99dbaf018


####  python __main__.py /home/ntlpt-42/synthetic_data_gen/real_data/bank.csv /home/ntlpt-42/synthetic_data_gen/real_data/bank_synth_epoch_1_test_2.csv  --discrete /home/ntlpt-42/synthetic_data_gen/real_data/bank.csv