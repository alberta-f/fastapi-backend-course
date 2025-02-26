from fastapi import FastAPI
import requests


class TaskTracker:
    JSON_API_URL='https://api.jsonbin.io/v3/b/67bf38a4e41b4d34e49d1a32'

    def __init__(self):
        self.tasks = self.load_tasks()


    def load_tasks(self):  
        response = requests.get(self.JSON_API_URL, headers={"X-Master-Key": "$2a$10$JxRxV.l5ecxD7r4BNJp5/Od.22A1TlqgdLRUfhN73oSaCMQQ9SMkq"})
        return response.json().get('record', {})


    def dump_tasks(self): 
        requests.put(self.JSON_API_URL, json=self.tasks, headers={"X-Master-Key": "$2a$10$JxRxV.l5ecxD7r4BNJp5/Od.22A1TlqgdLRUfhN73oSaCMQQ9SMkq"})
    

    def add_task(self, task, done):
        new_id = max(map(int, self.tasks.keys()), default=0) + 1
        new_id = str(new_id)

        llm_response = llm_client.process_task(task)
        explanation = llm_response.get("result", {}).get("response", "LLM не смог дать ответ.")
        task = f'{task}, {explanation}'

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


class LLMClient():
    LLM_API_URL = 'https://api.cloudflare.com/client/v4/accounts/f4b07696c503717ccc919e44f454ded1/ai/run/'
    headers = {"Authorization": "Bearer KAj0xrVIDWmgLD0b1dHLpvFBOavtume7IGTQIgvu"}
    model = '@cf/meta/llama-3-8b-instruct'

    def __init__(self):
        self.inputs = []
        self.initialized = False


    def add_input(self, content, role='user'):
        self.inputs.append({"role": role, "prompt": content})


    def run(self):
        input = {"prompt": self.inputs}
        response = requests.post(f"{self.LLM_API_URL}{self.model}", headers=self.headers, json=input)
        return response.json()
    

    def process_task(self, task_text: str):
        self.inputs = []
        
        if not self.initialized:
            self.inputs.append({"role": "system", "prompt": "You are an AI assistant that helps solve tasks by generating step-by-step solutions."})
            self.initialized = True
        
        self.add_input(f"Explain how to solve this task: {task_text}")
        return self.run()


app = FastAPI()
task_tracker = TaskTracker()
llm_client = LLMClient()


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
