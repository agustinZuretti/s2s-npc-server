import os 
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from melo.api import TTS
from OpenVoice.openvoice.api import BaseSpeakerTTS, ToneColorConverter
from OpenVoice.openvoice import se_extractor
import os
import torch

# Ruta base desde donde se ejecuta el script actual
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
device = "cuda:0" if torch.cuda.is_available() else "cpu"

# Paths para la version 2 del embbeding 
config_path_v2 = os.path.join(base_dir, 'OpenVoice', 'checkpoints_v2', 'converter', 'config.json')
ckpt_path_v2 = os.path.join(base_dir, 'OpenVoice', 'checkpoints_v2', 'converter', 'checkpoint.pth')

# Base speaker v2 español path
src_se_spanish_path = os.path.join(base_dir, 'OpenVoice', 'checkpoints_v2', 'base_speakers', 'ses', 'es.pth')

# Base speaker v2 ingles path
src_se_english_path = os.path.join(base_dir, 'OpenVoice', 'checkpoints_v2', 'base_speakers', 'ses', 'en-newest.pth')


# # Paths para la version 1
# config_path_v1= os.path.join(base_dir, 'OpenVoice', 'checkpoints', 'converter', 'config.json')
# ckpt_path_v1 = os.path.join(base_dir, 'OpenVoice', 'checkpoints', 'converter', 'checkpoint.pth')


# El tone color converter es el mismo en ambos casos (v1 y v2, pero la configuracion del checkpoint es diferente)
# tone_color_converter = ToneColorConverter(config_path_v2, device=device)
# tone_color_converter.load_ckpt(ckpt_path_v2)


# ckpt_base_path_v1 = os.path.join(base_dir, 'OpenVoice', 'checkpoints', 'base_speakers', 'EN')

# base_speaker_v1 = BaseSpeakerTTS(f'{ckpt_base_path_v1}/config.json', device=device)
# base_speaker_v1.load_ckpt(f'{ckpt_base_path_v1}/checkpoint.pth')

# source_se_v1 = torch.load(f'{ckpt_base_path_v1}/en_default_se.pth').to(device)


def load_tone_color_converter(speaker_name: str, version: str):

    tone_color_converter = ToneColorConverter(config_path_v2, device=device)
    tone_color_converter.load_ckpt(ckpt_path_v2)
    
    reference_speaker_path = os.path.join(base_dir,'OpenVoice','resources')
    reference_speaker = os.path.join(reference_speaker_path, f'{speaker_name}.mp3')
    target_se, audio_name = se_extractor.get_se(reference_speaker, tone_color_converter, vad=False)
    print(f"Speaker {speaker_name} loaded successfully.")
    return target_se, tone_color_converter


def generate_audio_response(text, language, target_se, tone_color_converter):

    if language == 'en':
        src_se = torch.load(src_se_english_path, map_location=device)
        tts_model = TTS(language='EN_NEWEST',  device=device)
    else:
        src_se = torch.load(src_se_spanish_path, map_location=device)
        tts_model = TTS(language='ES',  device=device)
        speed= 0.90


    output_directory = "outputs_v2"
    os.makedirs(output_directory, exist_ok=True)  # Asegurar que el directorio existe


    speaker_ids = tts_model.hps.data.spk2id
   

    for speaker_key in speaker_ids.keys():
        speaker_id = speaker_ids[speaker_key]
        normalized_speaker_key = speaker_key.lower().replace('_', '-')
        
        # Generar audio
        src_path = os.path.join(output_directory, f'tmp_{normalized_speaker_key}.wav')
        output_path = os.path.join(output_directory, f'output_v2_{normalized_speaker_key}.wav')
        tts_model.tts_to_file(text, speaker_id, src_path, speed=0.84)
        
        # Convertir tono y color de voz
        encode_message = "@MyShell"
        tone_color_converter.convert(audio_src_path=src_path, 
                                     src_se=src_se, 
                                     tgt_se=target_se, 
                                     output_path=output_path, 
                                     message=encode_message)

        # Leer el archivo generado y devolver los bytes
        if os.path.exists(output_path):
            with open(output_path, 'rb') as f:
                audio_data = f.read()
            print(f"Archivo de audio guardado exitosamente en {output_path}")
            return audio_data 


    
    
    # raise Exception("No se generó ningún archivo de audio.")

# async def generate_audio_response(text):
   
#     output_directory = "outputs_v3"
#     src_path = os.path.join(output_directory, f'tmp_es.wav')

#     os.makedirs(output_directory, exist_ok=True)  # Asegurar que el directorio existe
#     base_speaker_tts.tts(text, src_path, speaker='default', language='English', speed=0.94)    

#     save_path = f'{output_directory}/output_en_default.wav'
#     output_path = os.path.join(output_directory, f'output_en_default.wav')

#     # Run the tone color converter
#     encode_message = "@MyShell"
#     tone_color_converter.convert(
#         audio_src_path=src_path, 
#         src_se=source_se, 
#         tgt_se=target_se, 
#         output_path=save_path,
#         message=encode_message)
#         # Leer el archivo generado y devolver los bytes
    
#     if os.path.exists(output_path):
#         with open(output_path, 'rb') as f:
#             audio_data = f.read()
#         print(f"Archivo de audio guardado exitosamente en {output_path}")
#         return audio_data  # Retorna después de procesar el primer speaker válido

#     # raise Exception("No se generó ningún archivo de audio.")