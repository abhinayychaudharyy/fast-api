from fastapi import FastAPI,Path,HTTPException,Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, computed_field
from typing import Annotated,Literal,Optional
import json


app=FastAPI()

class Patient(BaseModel):
    
    id:Annotated[str,Field(...,description="Id of the patient",examples=["P001"])]
    name:Annotated[str,Field(...,description="name of the patient")]
    city:Annotated[str,Field(...,description="City of the patient living")]
    age:Annotated[int,Field(...,description="Age of the patient")]
    gender:Annotated[Literal['male','female','other'],Field(...,description="gender of the patient")]
    height:Annotated[float,Field(...,gt=0,description="height of the patient")]
    weight:Annotated[float,Field(...,gt=0,description="weight of the patient")]
    
    @computed_field
    @property
    def bmi(self) -> float:
        bmi=round(self.weight/(self.height**2),2)
        return bmi
    @computed_field
    @property
    def verdict(self) ->str:
        if self.bmi<18.5:
            return 'Underweight'
        elif self.bmi<25:
            return 'Normal'
        elif self.bmi<30:
            return 'Normal'
        else:
            return 'obese'

class PatientUpdate(BaseModel):
    name:Annotated[Optional[str],Field(default="None")]
    city:Annotated[Optional[str],Field(default="None")]
    age:Annotated[Optional[int],Field(default="None")]
    gender:Annotated[Optional[Literal['male','female','other']],Field(default="None")]
    height:Annotated[Optional[float],Field(default="None",gt=0)]
    weight:Annotated[Optional[float],Field(default="None",gt=0)]
    

def load_data():
    with open("patient.json","r") as f:
        data=json.load(f)
    return data

def save_data(data):
    with open("patient.json","w") as f:
        json.dump(data,f)
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


@app.post("/create")
def create_patient(patient:Patient):
    # load excisting data 
    data = load_data()
    #check if patient already exist
    if patient.id in data :
        return HTTPException(status_code=400,detail="Patient already exists")
    #new patient should be add to data base 
    
    data[patient.id]=patient.model_dump(exclude="id") 
    #so here model_dump use for converting the pydantic object to the python dict  type and we excluded id asit is the key for the json
    
    # save into the json file(Database)
    save_data(data)
    return JSONResponse(status_code=201,content={'message':'patient created succesfully'})

@app.put("/edit/{patient_id}")
def update_patient(patient_id:str , patient_update:PatientUpdate):
    data=load_data()
    if patient_id not in data:
        raise HTTPException(status_code=404,detail='Patient id not found')
    
    # excisting patient data 
    exsisting_patient_info=data[patient_id]
    
    update_patient_info=patient_update.model_dump(exclude_unset=True)  
    #here we use the  exclude_unset as we oinly need to update the feild that is given to use not entire thing 
    
    
    for key,value in update_patient_info.items():
        exsisting_patient_info[key]=value
        
    # esxisting_patiet_info -> pydantic object -> updated the bmi and the verdict -> pydantic object ->dict
        # and humne id isilye add kra kyuki jo hmare pass pehle existing_patient_info hai usme id nhi hai and but Patient vala pydantic class hai usme id required hai
    exsisting_patient_info['id']=patient_id
    patient_pydantic_obj=Patient(**exsisting_patient_info)
    exsisting_patient_info=patient_pydantic_obj.model_dump(exclude='id')
    
    # add this dict to data
    data[patient_id]=exsisting_patient_info
    save_data(data)
    return JSONResponse(status_code=200,content={'message':"update patient"})
    
    
    
@app.delete("/delete/{patient_id}")
def delete_patient(patient_id:str):
    # load the data
    data=load_data()
    
    if patient_id not in data:
        raise HTTPException(status_code=404,detail="Patient not found")
    
    del data[patient_id]
    
    save_data(data)
    
    return JSONResponse(status_code=200,content={'message':'patient deleted'})
