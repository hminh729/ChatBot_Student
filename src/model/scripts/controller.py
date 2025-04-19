from pydantic import BaseModel,Field
import motor.motor_asyncio
from fastapi.encoders import jsonable_encoder
from typing import List
from fastapi import Body
from fastapi import Path


class Message(BaseModel):
    role: str 
    content: str
class Subject(BaseModel):
    subjectId: str 
    subjectName: str 
    messages: List[Message]

class User(BaseModel):
    fullName: str
    userId: str
    fbLink: str
    subject: List[Subject] = Field(default_factory=list)

#Conect to MongoDB
client = motor.motor_asyncio.AsyncIOMotorClient()
client = motor.motor_asyncio.AsyncIOMotorClient("mongodb+srv://phamminh7292004:Emh1ozB80dM675ve@cluster0.un3mk.mongodb.net/Auth?retryWrites=true&w=majority&appName=Cluster0")
db = client.Auth
db = client["Auth"]

collection = db.Users
collection = db["Users"]

async def signup(user: User):
    
    thisUser = jsonable_encoder(user)
    result = await collection.insert_one(thisUser)
    return {"status": "success", "user_id": str(result.inserted_id)}


async def get_message(user_id :str = Path(...), subject_id: str = Path(...)):
    thisUser = await collection.find_one({"userId": user_id})
    if not thisUser:
        return {
            "status": "fail",
            "message": "User not found"
        }
    for subject in thisUser.get("subject", []):
        if subject["subjectId"] == subject_id:
            return {
                "status": "success",
                "messages": subject.get("messages", [])
            }
    return {
        "status": "fail",
        "message": "Subject not found"
    }
async def update_message(user_id :str = Path(...), subject_id: str = Path(...) ,messages: List[Message] = Body(...) ):
    
    message_json = jsonable_encoder(messages)
    result = await collection.find_one_and_update(
        {"userId": user_id, "subject.subjectId": subject_id},
        {"$set": {"subject.$.messages":message_json}}
    )
    if result:
        return {
            "status": "success",
            "message": "Message updated successfully"
        }
    else:
        return {
            "status": "fail",
            "message": "Error on updating message"
        }

async def add_subject(
    user_id: str = Path(...),
    subject_id: str = Body(...),
    subject_name: str = Body(...)
):
    new_subject = {
        "subjectId": subject_id,
        "subjectName": subject_name,
        "messages": []
    }

    result = await collection.update_one(
        {"userId": user_id},
        {"$push": {"subject": new_subject}}
    )

    if result.modified_count == 0:
        return {"status": "fail", "message": "User not found or subject not added"}
    
    return {"status": "success", "message": "Subject added successfully"}