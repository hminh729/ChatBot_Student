from pydantic import BaseModel,Field
import motor.motor_asyncio
from fastapi.encoders import jsonable_encoder
from typing import List
from fastapi import Body
from fastapi import Path
from fastapi import UploadFile, File, HTTPException
from starlette.concurrency import run_in_threadpool
import os
from fastapi import Form
import shutil
from langchain_core.messages import HumanMessage, AIMessage
from scripts.agent import get_llm_and_agent, get_retriever
from scripts.seed_data import seed_data_milvus_ollama, delete_collection 

# Mô hình dữ liệu cho người dùng và môn học
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

#Conect to MongoDB Atlas
client = motor.motor_asyncio.AsyncIOMotorClient()
client = motor.motor_asyncio.AsyncIOMotorClient("mongodb+srv://phamminh7292004:Emh1ozB80dM675ve@cluster0.un3mk.mongodb.net/Auth?retryWrites=true&w=majority&appName=Cluster0")
db = client.Auth
db = client["Auth"]

collection = db.Users
collection = db["Users"]

# Hàm đăng ký người dùng mới
async def signup(user: User):
    
    thisUser = jsonable_encoder(user)
    existing_user = await collection.find_one({"stu_id":thisUser["stu_id"]})
    if existing_user:
        return {"status": "fail", "message": "User already exists"}
    result = await collection.insert_one(thisUser)
    return {"status": "success", "user_id": str(result.inserted_id)}

# Hàm lấy danh sách messages của một môn học
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

# Hàm cập nhật messages của một môn học
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

# Hàm thêm môn học mới cho người dùng
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
    thisUser = await collection.find_one({"stu_id":stu_id})
    if not thisUser:
        return{"status":"fail",
                "message":"User not Found"}
    else:
        for subject in thisUser.get("subject",[]):
            if subject["subject_name"] == subject_name:
                return {
                    "status":"success",
                    "message":"Subject already exists"
                }    
    result = await collection.update_one(
        {"stu_id": stu_id},
        {"$push": {"subject": new_subject}}
    )
    if result.modified_count == 0:
        return {"status": "fail", "message": "User not found or subject not added"}
    return {"status": "success", "message": "Subject added successfully"}

# Hàm xử lý upload file PDF
async def post_file(file: UploadFile = File(...), subject_name: str = Form(...), stu_id: str = Form(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Chỉ hỗ trợ file PDF.")

    save_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data"))
    os.makedirs(save_dir, exist_ok=True)
    file_path = os.path.join(save_dir, file.filename)

    collection = subject_name + stu_id

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        print(f"File saved to {file_path}") 

        await run_in_threadpool(
            seed_data_milvus_ollama,
            file_path, 
            "bge-m3:567m",
            collection,
            "http://milvus-standalone:19530"
        )

        return {"message": "Upload thành công", "filename": file.filename}

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Lỗi khi lưu file: {str(e)}")

# Hàm đăng nhập người dùng
async def login(stu_id:str = Path(...), password:str = Path(...)):
    thisUser = await collection.find_one({"stu_id": stu_id})

    if not thisUser:
        return {
            "status": "fail",
            "message": "User not found"
        }
    else:
        if thisUser["password"] != password:
            return {
                "status":"fail",
                "message": "Password is incorrect"
            }
        else:
            
            return {
                "status":"success",
                "message": "Login successfully",
            }
# Hàm lấy phản hồi từ chatbot Agent
async def get_response(
    stu_id: str = Path(...),
    subject_name: str = Path(...),
    input: str = Form(...)
):
    retriever = get_retriever(subject_name+stu_id)
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

# Hàm lấy danh sách các môn học của người dùng
async def get_subjects(stu_id :str = Path(...)):
    
    thisUser = await collection.find_one({"stu_id": stu_id})
    subjects = []
    if not thisUser:
        return {
            "status": "fail",
            "message": "User not found"
        }
    for subject in thisUser.get("subject", []):
        subjects.append(subject["subject_name"])
    return {
        "status": "success",
        "subjects": subjects
    }

# Hàm xóa môn học của người dùng
async def delete_subject(stu_id : str = Path(...), subject_name:str = Path(...)):
    try:
        await collection.update_one(
            {"stu_id": stu_id},
            {"$pull": {"subject": {"subject_name": subject_name}}}
        )

        collection_name = subject_name + stu_id
        delete_collection(collection_name)
        return {
            "status":"success",
            "message":"Delete subject successfully"
        }
        
    except Exception as e:
        return{
            "status":"fail",
            "message":"Server error"
        }