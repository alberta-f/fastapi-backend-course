from fastapi import FastAPI, HTTPException
import requests


class BaseHTTPClient:
    def get(self, url, headers=None):
        try:    
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            return response.json()

        except requests.RequestException as e:
            raise HTTPException(status_code=500, detail=f"Ошибка при GET-запросе: {str(e)}")


    def post(self, url, data, headers=None):
        try:
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()

            return response.json()

        except requests.RequestException as e:
            raise HTTPException(status_code=500, detail=f"Ошибка при POST-запросе: {str(e)}")

    def put(self, url, data, headers=None):
        try:
            response = requests.put(url, json=data, headers=headers)
            response.raise_for_status()

        except requests.RequestException as e:
            raise HTTPException(status_code=500, detail=f"Ошибка при PUT-запросе: {str(e)}")


class TaskTracker(BaseHTTPClient):
    JSON_API_URL='https://api.jsonbin.io/v3/b/67bf38a4e41b4d34e49d1a32'
    HEADERS={"X-Master-Key": "$2a$10$JxRxV.l5ecxD7r4BNJp5/Od.22A1TlqgdLRUfhN73oSaCMQQ9SMkq"}

    def __init__(self):
        self.tasks = self.load_tasks()


    def load_tasks(self): 
        return self.get(self.JSON_API_URL, headers=self.HEADERS).get('record', {})


    def dump_tasks(self): 
        self.put(self.JSON_API_URL, self.tasks, headers=self.HEADERS)


    def add_task(self, task, done):
        if not task:
            raise HTTPException(status_code=400, detail="Текст задачи не может быть пустым")

        new_id = max(map(int, self.tasks.keys()), default=0) + 1
        new_id = str(new_id)

        try:
            llm_response = llm_client.process_task(task)
            explanation = llm_response.get("result", {}).get("response", "LLM не смог дать ответ.")
        
        except:
            raise HTTPException(status_code=500, detail="Ошибка взаимодействия с LLM API")

        self.tasks[new_id] = {"task": f'{task}, {explanation}', "done": done}  
        self.dump_tasks()
        return new_id
    

    def update_task(self, task_id: str, task: str = None, done: bool = None):
        if task_id not in self.tasks:
            raise HTTPException(status_code=404, detail='Задача не найдена')

        if task is not None:
            self.tasks[task_id]["task"] = task

        if done is not None:
            self.tasks[task_id]["done"] = done

        self.dump_tasks()
        return self.tasks[task_id]
    

    def delete_task(self, task_id: str):
        if task_id not in self.tasks:
            raise HTTPException(status_code=404, detail='Задача не найдена')

        del self.tasks[task_id]
        self.dump_tasks()


class LLMClient(BaseHTTPClient):
    LLM_API_URL = 'https://api.cloudflare.com/client/v4/accounts/f4b07696c503717ccc919e44f454ded1/ai/run/'
    HEADERS = {"Authorization": "Bearer KAj0xrVIDWmgLD0b1dHLpvFBOavtume7IGTQIgvu"}
    MODEL = '@cf/meta/llama-3-8b-instruct'


    def __init__(self):
        self.messages = []


    def add_message(self, content, role='user'):
        self.messages.append({"role": role, "content": content})


    def run(self):
        payload = {"messages": self.messages}
        return self.post(f"{self.LLM_API_URL}{self.MODEL}", payload, headers=self.HEADERS)
    

    def process_task(self, task_text: str):
        self.messages = []

        self.add_message("You are an AI assistant that helps solve tasks by generating step-by-step solutions.", role="system")
        self.add_message(f"Explain how to solve this task: {task_text}", role="user")

        return self.run()


app = FastAPI()
task_tracker = TaskTracker()
llm_client = LLMClient()


@app.get("/tasks", status_code=200)  
def get_tasks():
    return task_tracker.tasks


@app.post("/tasks", status_code=201)  
def create_task(task: str, done: bool = False):
    new_id = task_tracker.add_task(task, done)
    return {"message": "Задача добавлена", "task_id": new_id, "task": task_tracker.tasks[new_id]}


@app.put("/tasks/{task_id}", status_code=200)  
def update_task(task_id: str, task: str = None, done: bool = None):
    updated_task = task_tracker.update_task(task_id, task, done)

    return {"message": "Задача обновлена", "task": updated_task}


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: str):
    task_tracker.delete_task(task_id)

    return {"message": "Задача удалена"}
