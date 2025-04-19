from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from controller import signup, get_message, update_message, add_subject

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
app.post("/signup/")(signup)
app.get("/get_message/{user_id}/{subject_id}")(get_message)
app.post("/update_message/{user_id}/{subject_id}")(update_message)
app.post("/add_subject/{user_id}")(add_subject)
