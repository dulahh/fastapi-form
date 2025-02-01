from fastapi import FastAPI, HTTPException, Path, Query, Body, Request
from pydantic import BaseModel, EmailStr, validator
from typing import List, Optional
import uvicorn
import re

app = FastAPI()


data_store = {
    "students": {}
}


def semester_validation(semester: Optional[str]) -> bool:
    if semester is None:
        return True
    pattern = r"^(Fall|spring|summer)\d{4}$"
    return bool(re.match(pattern, semester))


class RegisterStudent(BaseModel):
    name: str
    email: EmailStr
    age: int
    courses: List[str]  # Corrected the type hint

    @validator("courses")
    def check_courses(cls, courses):
        if len(courses) < 1 or len(courses) > 5:
            raise ValueError("Courses must be between 1 and 5 items.")
        if len(courses) != len(set(courses)):
            raise ValueError("Duplicate courses are not allowed.")
        for course in courses:  # Fixed variable name issue
            if not (5 <= len(course) <= 30):
                raise ValueError("Course name should be between 5-30 characters.")
        return courses


@app.get("/students/{student_id}")
def get_student_information(student_id: int, include_grades: bool, semester: Optional[str] = None):
    try:
        if student_id not in data_store["students"]:
            raise ValueError(status_code=404, detail="Student not found.")

        student = data_store["students"][student_id]
        response = {
            "student_id": student_id,
            "name": student["name"],
            "email": student["email"]
        }

        if include_grades:
            response["grades"] = student.get("grades", {})

        if not semester_validation(semester):
            raise ValueError(status_code=400, detail="Semester format is invalid.")

        response["semester"] = semester
        return response

   

    except Exception as e:
        return {
            "status": "Error",
            "detail": None,
            "message": str(e)
        }


@app.post("/students/register")
async def register_student(student: RegisterStudent):
    new_id = max(data_store["students"].keys() or [1000]) + 1
    data_store["students"][new_id] = student.dict()  
    return {
        "student_id": new_id,
        "message": "Student registered successfully."
    }