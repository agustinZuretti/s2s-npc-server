import sys
import os
import uvicorn
from fastapi import FastAPI
import warnings

current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')
if src_path not in sys.path:
    sys.path.append(src_path)

from fastapi.openapi.docs import get_swagger_ui_html
from services.transcriber import router as transcriber_router
from services.conversations import router as conversation_router

PORT = 8000

app = FastAPI(docs_url="/docs", redoc_url=None, openapi_url="/openapi.json")

app.include_router(transcriber_router)
app.include_router(conversation_router)
warnings.filterwarnings("ignore", category=UserWarning, module="torch.nn.modules.conv")

# Suprimir warnings específicos
warnings.filterwarnings(
    "ignore",
    message="torch.nn.utils.weight_norm is deprecated in favor of torch.nn.utils.parametrizations.weight_norm."
)
warnings.filterwarnings(
    "ignore",
    message="stft with return_complex=False is deprecated. In a future pytorch release, stft will return complex tensors for all inputs, and return_complex=False will raise an error."
)
warnings.filterwarnings(
    "ignore",
    message="Plan failed with a cudnnException: CUDNN_BACKEND_EXECUTION_PLAN_DESCRIPTOR: cudnnFinalize Descriptor Failed cudnn_status: CUDNN_STATUS_NOT_SUPPORTED"
)

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(openapi_url="/openapi.json", title="Custom Swagger UI")

@app.get("/")
async def root():
    return {"message": "Hello World"}

if __name__ == "__main__":
    uvicorn.run(app, host="192.168.1.61", port=PORT)
