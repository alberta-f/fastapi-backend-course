from fastapi import FastAPI

app = FastAPI()

tasks = {
    1: {"task": "Купить хлеб", "done": True},
    2: {"task": "ДЗ по ООП", "done": False},
}

@app.get("/tasks")  
def get_tasks():
    return tasks  

@app.post("/tasks")  
def create_task(task: str, done: bool = False):
    new_id = max(tasks.keys(), default=0) + 1  
    tasks[new_id] = {"task": task, "done": done}  
    return {"message": "Задача добавлена", "task_id": new_id, "task": tasks[new_id]}

@app.put("/tasks/{task_id}")  
def update_task(task_id: int, task: str = None, done: bool = None):
    if task_id in tasks:
        if task is not None:
            tasks[task_id]["task"] = task
        if done is not None:
            tasks[task_id]["done"] = done
        return {"message": "Задача обновлена", "task": tasks[task_id]}
    return {"message": "Задача не найдена"}

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    if task_id in tasks:
        del tasks[task_id]
        return {"message": "Задача удалена"}
    return {"message": "Задача не найдена"}
