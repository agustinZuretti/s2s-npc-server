import asyncio
import websockets

async def send_audio_and_receive_audio(uri, input_audio_path, output_audio_path):
    async with websockets.connect(uri) as websocket:
        # Leer el archivo de audio local y enviarlo
        with open(input_audio_path, "rb") as audio_file:
            audio_data = audio_file.read()
        print("Enviando audio al servidor...")
        await websocket.send(audio_data)

        # Recibir la respuesta de audio del servidor
        print("Esperando audio generado del servidor...")
        response_audio = await websocket.recv()
        
        # Verificar y manejar si la respuesta es una cadena
        if isinstance(response_audio, str):
            # Convertir de cadena a bytes si es necesario (este paso puede necesitar ajustes basados en cómo el servidor codifica los bytes a cadena)
            response_audio = bytes(response_audio, 'utf-8')
        
        print("Audio recibido, guardando...")
        with open(output_audio_path, "wb") as output_file:
            output_file.write(response_audio)
        print("Audio guardado exitosamente en:", output_audio_path)
        await websocket.close()
# Ruta al servidor WebSocket
server_uri = "ws://192.168.1.64:8001/ws/audio"

# Ruta al archivo de audio que quieres enviar y donde guardar la respuesta
input_audio_path = "hola.wav"
output_audio_path = "path_to_save_received_audio.wav"

# Ejecutar el cliente para enviar y recibir audio
asyncio.get_event_loop().run_until_complete(send_audio_and_receive_audio(server_uri, input_audio_path, output_audio_path))


