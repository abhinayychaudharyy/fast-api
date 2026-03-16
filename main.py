from fastapi import FastAPI,Path,HTTPException,Query
from pydantic import BaseModel,Field
from typing import Annotated,Literal
import json


app=FastAPI()

class Patient(BaseModel):
    
    id:Annotated[str,Field(...,description="Id of the patient",examples=["P001"])]
    name:Annotated[str,Field(...,description="name of the patient")]
    city:Annotated[str,Field(...,description="City of the patient living")]
    age:Annotated[int,Field(...,description="Age of the patient")]
    gender:Annotated[Literal['male','female','other'],Field(...,description="gender of the patient")]
    height:Annotated[float,Feild(...,gt=0,description="height of the patient")]
    weight:Annotated[float,Field(...,gt=0,description="weight of the patient")]

def load_data():
    with open("patient.json","r") as f:
        data=json.load(f)
    return data
@app.get("/")
def hello():
    return {"message":"Patient Management system api"}

@app.get("/about")
def about():
    return {"message":"A fully functional api to manage your patient record"}

@app.get("/view")
def view():
    data=load_data()
     
    return data

@app.get("/patient/{patient_id}")
def  view_patient(patient_id:str = Path(...,description="ID of the patient in the json",examples="P001")):
    data=load_data()
    if patient_id in data:
        return data[patient_id]
    raise HTTPException(status_code=404,detail="Patient not found")

@app.get("/sort")
def sort_patients(sort_by:str = Query(...,description="sort on the basis of the bmi,weight or height"),order:str=Query("asc",description="sort in the asc or descending")):
    valid_feilds=['height','age','bmi']
    if sort_by not in valid_feilds:
        raise HTTPException(status_code=400,detail=f"invalid feilds select from {valid_feilds}")
    if order not in ['asc','desc']:
        raise HTTPException(status_code=400,detail="Invalid order select from asc or desc")
    sort_order= True if order=='desc' else False
    data=load_data()
    sorted_data=sorted(data.values(),key=lambda x:x.get(sort_by,0),reverse=sort_order)
    return sorted_data