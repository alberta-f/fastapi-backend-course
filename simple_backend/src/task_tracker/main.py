from fastapi import FastAPI
from pathlib import Path
import json


class TaskTracker:
    def __init__(self, file='tasks.json'):
        self.file = Path(file)
        self.tasks = self.load_tasks()


    def load_tasks(self):
        if self.file.exists():
            with open('tasks.json', 'r', encoding='utf8') as data:
                return json.load(data)

        return {}


    def dump_tasks(self):
        with open('tasks.json', 'w', encoding='utf8') as file:
            json.dump(self.tasks, file, indent=4)

    
    def add_task(self, task, done):
        new_id = max(map(int, self.tasks.keys()), default=0) + 1
        new_id = str(new_id)

        self.tasks[new_id] = {"task": task, "done": done}  

        self.dump_tasks()

        return new_id
    

    def update_task(self, task_id: str, task: str = None, done: bool = None):
        task_id = str(task_id)

        if task_id in self.tasks:
            if task is not None:
                self.tasks[task_id]["task"] = task

            if done is not None:
                self.tasks[task_id]["done"] = done

            self.dump_tasks()

            return True
        
        return False
    

    def delete_task(self, task_id: str):
        task_id = str(task_id)

        if task_id in self.tasks:
            del self.tasks[task_id]

            self.dump_tasks()

            return True
        
        return False


app = FastAPI()
task_tracker = TaskTracker()

@app.get("/tasks")  
def get_tasks():
    return task_tracker.tasks


@app.post("/tasks")  
def create_task(task: str, done: bool = False):
    new_id = task_tracker.add_task(task, done)
    return {"message": "Задача добавлена", "task_id": new_id, "task": task_tracker.tasks[new_id]}


@app.put("/tasks/{task_id}")  
def update_task(task_id: str, task: str = None, done: bool = None):
    if task_tracker.update_task(task_id, task, done):
        return {"message": "Задача обновлена", "task": task_tracker.tasks[task_id]}
    return {"message": "Задача не найдена"}


@app.delete("/tasks/{task_id}")
def delete_task(task_id: str):
    if task_tracker.delete_task(task_id):
        return {"message": "Задача удалена"}
    return {"message": "Задача не найдена"}
