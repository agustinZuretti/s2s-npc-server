import os
import sys
import torch

print(f"CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"CUDA device count: {torch.cuda.device_count()}")
    print(f"CUDA device name: {torch.cuda.get_device_name(0)}")

import os
import nvidia.cublas.lib
import nvidia.cudnn.lib

print(os.path.dirname(nvidia.cublas.lib.__file__))
print(os.path.dirname(nvidia.cudnn.lib.__file__))
#  Añade el directorio actual a sys.path
current_dir = os.path.abspath(os.path.dirname(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)


# from app.main import main_function  # Importa la función principal de tu aplicación

# if __name__ == "__main__":
#     main_function()  # Ejecuta la función principal de tu aplicación
