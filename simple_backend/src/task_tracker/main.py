from fastapi import FastAPI
import requests, json


class TaskTracker:
    API_URL='https://api.jsonbin.io/v3/b/67bf3b70acd3cb34a8f14db1'

    def __init__(self):
        self.tasks = self.load_tasks()


    def load_tasks(self):  
        response = requests.get(self.API_URL, headers={"X-Master-Key": "$2a$10$JxRxV.l5ecxD7r4BNJp5/Od.22A1TlqgdLRUfhN73oSaCMQQ9SMkq"})
        return response.json().get("record", {}) 


    def dump_tasks(self): 
        requests.put(self.API_URL, json={"record": self.tasks}, headers={"X-Master-Key": "$2a$10$JxRxV.l5ecxD7r4BNJp5/Od.22A1TlqgdLRUfhN73oSaCMQQ9SMkq"})
    

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
