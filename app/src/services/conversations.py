from fastapi import APIRouter, HTTPException
from ollama import Client, Options
from fastapi import FastAPI
from typing import Coroutine, List, Optional, Dict, Any
from pydantic import BaseModel
import os
import json

base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
modelfiles_path = os.path.join(base_dir, 'app', 'modelfiles')

router = APIRouter()
app = FastAPI()

def parse_inventory_string(inventory_string):
    try:
        inventory_json = json.loads(inventory_string)
        return inventory_json
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return None
    
class Item(BaseModel):
    name: str
    quantity: int
    type: str
    price: int
    
class NPCInventory(BaseModel):
    npc_id: str
    inventory: List[Item]

class ItemUpdate(BaseModel):
    updates: Dict[str, Any]

class BaseLLModel():
    modelfile: str
    host: str

    def __init__(self, model_name: str, host: str, host2: str):
        self.model_name = model_name
        self.host = host
        self.host2 = host2
        self.context_window = []

    def async_init(self):
        
        model_path = os.path.join(modelfiles_path, self.model_name + '.txt')
        print(f"model_path: {model_path}")
        client = Client(host=self.host)  
        # client.delete(model=self.model_name)
        client.create(model=self.model_name, path=model_path)
        client.generate(model=self.model_name) 

        self.add_user_message("hello sir")
        print("hello sir")

        try:
            client = Client(host=self.host)  # Ensure to await the async call
            response = client.chat(
                model=self.model_name,
                messages=self.context_window,
                keep_alive='10h',
                stream=False
            )
            self.add_assistant_message(response['message']['content'])
            print(f"respuesta recibida: {response['message']['content']}")

            print("mensaje de iniciazlizacion cargado")
        except Exception as e:
            return f"Error al generar la respuesta: {e}"
        # warm up the model
        print(f"Model {self.model_name} is loading.")
            
    # Function to add user message to context_window list
    def add_user_message(self, message):
        self.context_window.append({"role": "user", "content": message})

    def add_system_message(self, message):
        self.context_window.append({"role": "system", "content": message})

    def add_assistant_message(self, assistant_response):
        self.context_window.append({"role": "assistant", "content": assistant_response})

    # Function to add assistant message to context_window list
    def get_context_window(self):
        return self.context_window

    async def generate_response_from_model(self, content: str) -> str:
        
        self.add_user_message(content)

        try:
            client = Client(host=self.host)  # Ensure to await the async call
            response = client.chat(
                model=self.model_name,
                messages=self.context_window,
                keep_alive='20m',
                stream=False
            )

            self.add_assistant_message(response['message']['content'])

            
            # print(f'prompt_eval_count: {response["prompt_eval_count"]}')
            # print(f"prompt_eval_duration (seconds): {response['prompt_eval_duration']/10**9}")
            # print(f"eval_count: {response['eval_count']}")
            # print(f"tokens per second: {response['eval_count'] / response['prompt_eval_duration'] * 10**9} token/s")
        
        except Exception as e:
            return f"Error al generar la respuesta: {e}"

        return response['message']['content']
    
    async def get_image_context_from_model(self, image) -> str:
        
        print("store image in file")
        # store the image in a file
        with open('image-receive.jpg', 'wb') as f:
            f.write(image)
        try:
            client = Client(host=self.host2)
            
            response = client.generate(
                model='llava',
                prompt="focus on the npc in the image, and describe what his is doing.how is dressed? what is the person's expression? describe in detail the npc. do not tell that is from videogame. give a consise description of the npc. dont extend too much",
                images=[image],
                keep_alive='20m',
                options=Options(max_tokens=75),
                stream=False
            )
            self.add_system_message("<<PLAYER_DESCRIPTION>>" + response['response'] + "<<PLAYER_DESCRIPTION>>")
        
        except Exception as e:
            return f"Error al interpretar imagen: {e}"
        return response
    
    

class ServiceModel(BaseLLModel):

    async def update_inventory_status(self, voice_transcription:str, text_response: str) -> str:

        print("Updating inventory status")
        self.add_system_message("Player: " + voice_transcription)
        self.add_system_message("Charles: " + text_response)

        self.add_user_message("UPDATE INVENTORY")
        try:
            client = Client(host=self.host)  # Ensure to await the async call
            response = client.chat(
                model=self.model_name,
                messages=self.context_window,
                format='json',
                keep_alive='20m',
                stream=False
            )        
        except Exception as e:
            return f"Error al generar la respuesta: {e}"
        # print(f"enviando al inventario del vendedor: {response}")

        self.add_assistant_message(response['message']['content'])
        
        # print(self.context_window)
        return response['message']['content']
        
        # add to the context window the response from the service model to the seller model

    
