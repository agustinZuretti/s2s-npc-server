from fastapi import WebSocket, WebSocketDisconnect, APIRouter, HTTPException
from .voice import generate_audio_response, load_tone_color_converter
from .conversations import BaseLLModel, ServiceModel
from starlette.websockets import WebSocketState
from whisper import load_model
from scipy.io.wavfile import write
import numpy as np
import tempfile
import time
import json


OLLAMA_1 = "http://192.168.1.47:11434"
OLLAMA_2 = "http://192.168.1.55:11434"

# NPC = "charles"

SERVICE_MODEL_NAME = "service-model"

VISUAL_MODEL = "visual"

NPC = "mark4"

def parse_inventory_string(inventory_string):
    try:
        inventory_json = json.loads(inventory_string)
        return inventory_json
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return None

# Cargar el modelo y el conversor de tono y color de voz
target_se, tone_color_converter = load_tone_color_converter('joe', 'v2')

router = APIRouter()

# Cargar el modelo de transcripción
transcriber_model = load_model("medium.en")

# iniciar el modelo de conversación
conversation_model = BaseLLModel(model_name=NPC, host=OLLAMA_1, host2=OLLAMA_2)
print("Modelo de conversación cargado")
conversation_model.async_init()

# visual_model = BaseLLModel(model_name='llava', host=OLLAMA_2)
# print("Modelo visual cargado")
#visual_model.async_init()
# service_model = ServiceModel(model_name=SERVICE_MODEL_NAME, host=OLLAMA_1)
# print("Modelo de servicio cargado")
# service_model.async_init()


async def transcribe_audio(data: bytes):

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        audio_array = np.frombuffer(data, dtype=np.int16)
        write(tmp.name, 48000, audio_array)  
        tmp.flush()

        # print("Archivo temporal guardado")
        start_time = time.time()
        try:
            voice_transcription = transcriber_model.transcribe(tmp.name)
            # print(type(voice_transcription), voice_transcription['text'])
        except Exception as e:
            print(f"Error durante la transcripción: {e}")
            voice_transcription = "Transcripción falló debido a un error"
        
        end_time = time.time()
        # print(f"Tiempo de transcripción: {end_time - start_time:.2f} segundos")
        
        return voice_transcription
    
# @router.websocket("/ws/audio")
# async def websocket_audio_endpoint(websocket: WebSocket):
    
#     await websocket.accept()

    
    
#     try:
#         while True:
#             data = await websocket.receive()
            
#             if data["type"] == "websocket.receive":
#                 if "bytes" in data:
#                     audio_bytes = data["bytes"]
#                     try:
#                         if isinstance(audio_bytes, (bytes, bytearray)):

#                             print({"----------------- Ventada de contexto de Mark -----------------"})

#                             print (conversation_model.get_context_window())

#                             print({"------------------------------------------------------------------"})


#                             # print({"----------------- Ventada de contexto del service Model -----------------"})

#                             # print (service_model.get_context_window())

#                             # print({"------------------------------------------------------------------"})

#                             voice_transcription = await transcribe_audio(audio_bytes)

#                             print(f"Transcripción from the player: {voice_transcription['text']}")
                            
#                             text_response = await conversation_model.generate_response_from_model(voice_transcription['text'])
                            
#                             print(f"Model response: {text_response}")

#                             if "<call>" in text_response:
#                                 function_call_start = text_response.index("<call>") 
#                                 function_call_start_call= text_response.index("<call>") + len("<call>")
#                                 function_call_end = text_response.index("</call>")
#                                 function_call = text_response[function_call_start_call:function_call_end]
                                
#                                 # manda el sabor del helado
#                                 print(f"function_call: {function_call}")

#                                 text_response = text_response[:function_call_start]

#                                 await websocket.send_bytes(function_call)
                            
#                             audio_generated = generate_audio_response(text_response, 'en', target_se, tone_color_converter)
                            
#                             # update_message = await service_model.update_inventory_status(voice_transcription['text'], text_response)
                            
#                             # conversation_model.add_system_message(update_message)
                        
#                             # print(f"Inventory updated to charles from service: {update_message}")

#                             # print({"----------------- Ventada de contexto del service Model -----------------"})

#                             # print (service_model.get_context_window())

#                             # print({"------------------------------------------------------------------"})
                            
#                             print("    ")
#                             print("    ")
#                             print(f"Sending model response to the client: {text_response}")
#                             await websocket.send_bytes(audio_generated)
                        
#                         else:
#                             raise ValueError("El dato recibido no es de tipo bytes")
#                     except Exception as e:
#                         print(f"Error al procesar audio: {e}")
#                         await websocket.send_text(f"Error al procesar audio: {e}")
#                 else:
#                     print("Datos recibidos no contienen 'bytes'")
#             elif data["type"] == "websocket.disconnect":
#                 code = data["code"]
#                 print(f"Cliente desconectado con código: {code}")
#                 break
    
#     except WebSocketDisconnect:
#         print("Cliente desconectado")
#     except Exception as e:
#         print(f"Error en WebSocket: {e}")
#     finally:
#         try:
#             if websocket.client_state in [WebSocketState.DISCONNECTED, WebSocketState.CONNECTING]:
#                 await websocket.close()
#         except Exception as e:
#             print(f"Error al cerrar WebSocket: {e}")



# @router.get("/npc/inventory")
# async def get_npc_inventory():
#     inventory = await conversation_model.get_npc_inventory()
#     return parse_inventory_string(inventory)

# @router.post("/npc/event")
# async def post_npc_event(event: str):
#     await conversation_model.send_npc_event(event)
#     return {"message": "Evento enviado"}

# @router.post("/npc/inventory/add_item")
# async def add_item_to_inventory(item: Item):
#     event_message = f"ADD ITEM {json.dumps(item.dict())}"
#     response = await conversation_model.send_npc_event(event_message)
#     return {"message": response}
    
# @router.websocket("/ws/audio")
# async def websocket_audio_endpoint(websocket: WebSocket):
    
#     await websocket.accept()
    
#     try:
#         while True:
#             data = await websocket.receive()
            
#             if data["type"] == "websocket.receive":
#                 if "bytes" in data:
#                     audio_bytes = data["bytes"]
#                     try:
#                         if isinstance(audio_bytes, (bytes, bytearray)):
                            
#                             voice_transcription = await transcribe_audio(audio_bytes)
#                             print(f"voice_transcription: {voice_transcription['text'], voice_transcription['language']}")
                            
#                             text_response = await conversation_model.generate_response_from_model(voice_transcription['text'], voice_transcription['language'])
                            
#                             print(voice_transcription['language'])
#                             print(f"Model response: {text_response}")
                            
#                             audio_generated = generate_audio_response(text_response, voice_transcription['language'], target_se, tone_color_converter)
                            
#                             print(f"Sending model response: {text_response}")
#                             await websocket.send_bytes(audio_generated)
                        
#                         else:
#                             raise ValueError("El dato recibido no es de tipo bytes")
#                     except Exception as e:
#                         print(f"Error al procesar audio: {e}")
#                         await websocket.send_text(f"Error al procesar audio: {e}")
#                 else:
#                     print("Datos recibidos no contienen 'bytes'")
#             elif data["type"] == "websocket.disconnect":
#                 code = data["code"]
#                 print(f"Cliente desconectado con código: {code}")
#                 break
    
#     except WebSocketDisconnect:
#         print("Cliente desconectado")
#     except Exception as e:
#         print(f"Error en WebSocket: {e}")
#     finally:
#         try:
#             if websocket.client_state in [WebSocketState.DISCONNECTED, WebSocketState.CONNECTING]:
#                 await websocket.close()
#         except Exception as e:
#             print(f"Error al cerrar WebSocket: {e}")


import io
from PIL import Image
from fastapi import WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState

@router.websocket("/ws/audio")
async def websocket_audio_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    try:
        while True:
            data = await websocket.receive()
            
            if data["type"] == "websocket.receive":
                if "bytes" in data:
                    received_bytes = data["bytes"]
                    try:
                        await process_received_data(websocket, received_bytes)
                    except Exception as e:
                        print(f"Error processing data: {e}")
                        await websocket.send_text(f"Error processing data: {e}")
                else:
                    print("Received data does not contain 'bytes'")
            elif data["type"] == "websocket.disconnect":
                print(f"Client disconnected with code: {data['code']}")
                break
    
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"Error in WebSocket: {e}")
    finally:
        await close_websocket(websocket)

async def process_received_data(websocket: WebSocket, received_bytes: bytes):
    if isinstance(received_bytes, (bytes, bytearray)):
        data_type = determine_data_type(received_bytes)
        
        if data_type == "PNG":
            await process_png_image(websocket, received_bytes)
        elif data_type == "audio":
            await process_audio_data(websocket, received_bytes)
        else:
            raise ValueError("Unsupported data type")
    else:
        raise ValueError("The received data is not of type bytes")

def determine_data_type(data: bytes) -> str:
    try:
        image = Image.open(io.BytesIO(data))
        if image.format == 'PNG':
            return "PNG"
    except IOError:
        return "audio"

async def process_png_image(websocket: WebSocket, image_bytes: bytes):
    print("Received a PNG image")

    # Add your PNG processing logic here
    print("Processing image...")
    image_response = await conversation_model.get_image_context_from_model(image_bytes)
    print("Image processed")
    print(f"Image model response: {image_response}")


async def process_audio_data(websocket: WebSocket, audio_bytes: bytes):
    

    voice_transcription = await transcribe_audio(audio_bytes)
    print(f"Transcripción from the player: {voice_transcription['text']}")
    
    text_response = await conversation_model.generate_response_from_model(voice_transcription['text'])
    print(f"Model response: {text_response}")

    if "<call>" in text_response:
        function_call = extract_function_call(text_response)
        text_response = text_response[:text_response.index("<call>")]
        await websocket.send_bytes(function_call.encode())
    
    audio_generated = generate_audio_response(text_response, 'en', target_se, tone_color_converter)
    
    print("\n\nSending model response to the client:", text_response)

    print("Received audio data")
    print("----------------- Ventada de contexto de Mark -----------------")
    print(conversation_model.get_context_window())
    print("------------------------------------------------------------------")
    await websocket.send_bytes(audio_generated)

def extract_function_call(text_response: str) -> str:
    start = text_response.index("<call>") + len("<call>")
    end = text_response.index("</call>")
    return text_response[start:end]

async def close_websocket(websocket: WebSocket):
    try:
        if websocket.client_state in [WebSocketState.DISCONNECTED, WebSocketState.CONNECTING]:
            await websocket.close()
    except Exception as e:
        print(f"Error closing WebSocket: {e}")