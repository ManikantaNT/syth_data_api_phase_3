import time
from io import StringIO
from typing import List
import requests
import pandas as pd
from fastapi import FastAPI, UploadFile, File, Form, Depends
from pydantic import EmailStr, BaseModel
from pymongo import collection
from tasks import add_data
from utilities import get_database, read_from_azure
from conf import PATH



from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

app = FastAPI()

db = get_database()
collection = db["jobs"]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.post('/token')
async def token(form_data: OAuth2PasswordRequestForm= Depends()):
	return {'access_token': form_data.username+ 'token'}


# @app.get("/items/")
# async def read_items(token: str = Depends(oauth2_scheme)):
#     return {"token": token}
  
 






@app.post("/create_synthetic_data")
async def create_synthetic_data(num_rows: int, epochs: int, batch_size: int, generator_dim: int,
                                log_frequency: bool, embedding_dim: int, discriminator_dim: int, emails:EmailStr = Form(...),
								token: str = Depends(oauth2_scheme)
                                ):
	# try:
	# 	contents = file.file.read()
	# 	with open(file.filename, 'wb') as f:
	# 		f.write(contents)
	# except Exception:
	# 	return {"message": "There was an error uploading the file"}
	# finally:
	# 	file.file.close()
	# s = str(contents, 'utf-8')
	# data = StringIO(s)
	data= read_from_azure(PATH)
	df= data
	print(df.shape)
	
	# df= data.toPandas()
	# df = pd.read_csv(data)
	# print(emails)
	# print('############',emails)
	# print(df.head())



	

#emails[0].split(",")

	returned_id = collection.insert_one({"emails": emails,
										"status": "pending",
										"timestamp": time.time(),
										"epochs": epochs,
										"batch_size": batch_size,
										"embedding_dim": embedding_dim,
										"generator_dim": generator_dim,
										"discriminator_dim": discriminator_dim,
										"num_rows": num_rows}).inserted_id
	print("object id:", returned_id)
	task = add_data.delay(df.to_json(orient='records'),
						str(returned_id), num_rows, epochs, batch_size, generator_dim,
						log_frequency,
						embedding_dim, discriminator_dim, emails)
	return {
		"task_id": str(task.id), 
	    "status":"accepted"
	             
	}


@app.get('/get_status')
async def get_status(task_id:str):
	content = requests.get(url = f"http://127.0.0.1:5559/api/task/info/{task_id}")
	status= content.json()['state']

	return {'Task-Id':task_id , 'status':status}

