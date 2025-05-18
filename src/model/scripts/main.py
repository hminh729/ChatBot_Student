from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from controller import signup, get_message, update_message, add_subject,post_file, login,get_response, get_subjects,delete_subject

app = FastAPI()

origins = [
    "http://localhost:5173",
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
app.post("/signup")(signup)
app.post("/login/{stu_id}/{password}")(login)
app.get("/get_message/{stu_id}/{subject_name}")(get_message)
app.post("/update_message/{stu_id}/{subject_name}")(update_message)
app.post("/add_subject/{stu_id}")(add_subject)
app.post("/post_file")(post_file)
app.post("/get_response/{stu_id}/{subject_name}")(get_response)
app.get("/get_subjects/{stu_id}")(get_subjects)
app.post("/delete_subject/{stu_id}/{subject_name}")(delete_subject)



