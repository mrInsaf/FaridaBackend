import logging

from fastapi import FastAPI, HTTPException
import mysql.connector
from pydantic import BaseModel
from typing import Optional

from fastapi.middleware.cors import CORSMiddleware

from db import *

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешить запросы со всех источников. Лучше указать конкретные источники, если возможно.
    allow_credentials=True,
    allow_methods=["*"],  # Разрешить все методы (GET, POST, DELETE и т.д.)
    allow_headers=["*"],  # Разрешить все заголовки
)

@app.get("/groups/{teacher_id}")
async def get_groups_by_teacher_id(teacher_id: int):
    groups = select_groups_by_teacher_id(teacher_id)
    if not groups:
        raise HTTPException(status_code=404, detail="groups not found by specified teacher")
    return groups


@app.get("/students/group/{group_id}")
async def get_students_by_group(group_id: int):
    query = f"SELECT * FROM students WHERE group_id = {group_id}"
    students = select(query)

    if not students:
        raise HTTPException(status_code=404, detail="Students not found in the specified group")

    return students


class StudentCreateRequest(BaseModel):
    name: str
    group_id: int


@app.post("/students/")
async def add_student(student: StudentCreateRequest):
    try:
        print(f'Received data: {student}')

        group_name = select_group_name_by_id(student.group_id)
        print(f'Group name is: {group_name}')

        data = [student.name, group_name, student.group_id]
        student_id = insert("students", data)

        if student_id is None:
            raise HTTPException(status_code=500, detail="Failed to insert student")

        return {"message": "Student added successfully", "student_id": student_id}
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=f"Error adding student: {e}")


class StudentDeleteRequest(BaseModel):
    student_ids: list[int]


@app.delete("/students/")
async def delete_students_by_ids(request: StudentDeleteRequest):
    try:
        if not request.student_ids:
            raise HTTPException(status_code=400, detail="No student IDs provided")

        rows_affected = delete_students(request.student_ids)

        if rows_affected == 0:
            raise HTTPException(status_code=404, detail="No students deleted")

        return {"message": f"{rows_affected} students deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting students: {e}")


class StudentAddRequest(BaseModel):
    name: str
    group_id: int




if __name__ == "__farida_backend__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
