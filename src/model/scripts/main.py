from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from scripts.controller import signup, get_message, update_message, add_subject,post_file, login,get_response, get_subjects,delete_subject

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://nginx",
    "http://nginx:80"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return "you must signup to use AI free"

# Route từ controller
app.post("/api/signup")(signup)
app.post("/api/login/{stu_id}/{password}")(login)
app.get("/api/get_message/{stu_id}/{subject_name}")(get_message)
app.post("/api/update_message/{stu_id}/{subject_name}")(update_message)
app.post("/api/add_subject/{stu_id}")(add_subject)
app.post("/api/post_file")(post_file)
app.post("/api/get_response/{stu_id}/{subject_name}")(get_response)
app.get("/api/get_subjects/{stu_id}")(get_subjects)
app.post("/api/delete_subject/{stu_id}/{subject_name}")(delete_subject)



