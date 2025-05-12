from pydantic import BaseModel,Field
import motor.motor_asyncio
from fastapi.encoders import jsonable_encoder
from typing import List
from fastapi import Body
from fastapi import Path
from fastapi import APIRouter, UploadFile, File, HTTPException
from seed_data import seed_data_milvus_ollama
from starlette.concurrency import run_in_threadpool
import os
from fastapi import Form
import shutil
from langchain_core.messages import HumanMessage, AIMessage
import asyncio
from agent import get_llm_and_agent, get_retriever

        
    

class Message(BaseModel):
    role: str 
    content: str
class Subject(BaseModel):
    subjectId: str 
    subjectName: str 
    messages: List[Message]

class User(BaseModel):
    fullname: str
    stu_id: str
    password:str
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


async def get_message(stu_id :str = Path(...), subject_name: str = Path(...)):
    
    thisUser = await collection.find_one({"stu_id": stu_id})
    if not thisUser:
        return {
            "status": "fail",
            "message": "User not found"
        }
    for subject in thisUser.get("subject", []):
        if subject["subject_name"] == subject_name:
            return {
                "status": "success",
                "messages": subject.get("messages", [])
            }
    return {
        "status": "fail",
        "message": "Subject not found"
    }
async def update_message(stu_id :str = Path(...), subject_name: str = Path(...) ,messages: List[Message] = Body(...) ):
    
    message_json = jsonable_encoder(messages)
    result = await collection.find_one_and_update(
        {"stu_id": stu_id, "subject.subject_name": subject_name},
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
    stu_id: str = Path(...),
    subject_id: str = Body(...),
    subject_name: str = Body(...)
):
    new_subject = {
        "subject_id": subject_id,
        "subject_name": subject_name,
        "messages": []
    }

    result = await collection.update_one(
        {"stu_id": stu_id},
        {"$push": {"subject": new_subject}}
    )

    if result.modified_count == 0:
        return {"status": "fail", "message": "User not found or subject not added"}
    
    return {"status": "success", "message": "Subject added successfully"}

async def post_file(file: UploadFile = File(...), subject_name:str  = Form(...)):
    # Kiểm tra định dạng
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Chỉ hỗ trợ file PDF.")
    # Đường dẫn lưu file
    save_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data"))
    os.makedirs(save_dir, exist_ok=True)  # Tạo thư mục nếu chưa có
    file_path = os.path.join(save_dir, file.filename)
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        file_dir = "../data/" + file.filename
        await run_in_threadpool(
            seed_data_milvus_ollama,
            file_dir,
            "bge-m3:567m",
            subject_name,     
            "http://localhost:19530"
        )
        return {"message": "Upload thành công", "filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi lưu file: {str(e)}")


async def login():
    return "hi"

async def get_response(
    stu_id: str = Path(...),
    subject_name: str = Path(...),
    input: str = Form(...)
):
   
    retriever = get_retriever(subject_name)
    agent_executor = get_llm_and_agent(retriever)

    result = await get_message(stu_id, subject_name)
    mongo_mess_history = result.get("messages", [])
    thisUserMessage = {"role": "user", "content": input}
    input_chatbot = mongo_mess_history[-10:]   # Giới hạn số dòng lịch sử
    chat_history = []
    for msg in input_chatbot:
        if msg["role"] == "user":
            chat_history.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            chat_history.append(AIMessage(content=msg["content"]))

    response = agent_executor.invoke({
        "input": input,
        "chat_history": chat_history
    })

    thisAssistantMessage = {"role": "assistant", "content": response["output"]}
    mongo_mess_history.append(thisUserMessage)
    mongo_mess_history.append(thisAssistantMessage)


    await update_message(stu_id, subject_name, mongo_mess_history)

    return {
        "status": "success",
        "message": response["output"]
    }

