from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import numpy as np
import cv2
import zxingcpp
import secrets

security = HTTPBasic()

USERNAME = "bigworks"
PASSWORD = "1122334455"

app = FastAPI(
    title="QR Reader API",
    description="API para leitura de QR Code usando ZXing",
    version="1.0.0"
)

def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, USERNAME)
    correct_password = secrets.compare_digest(credentials.password, PASSWORD)

    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
            headers={"WWW-Authenticate": "Basic"},
        )

    return credentials.username


@app.post("/api/read-qrcode")
async def read_qrcode(
    file: UploadFile = File(...),
    _: str = Depends(authenticate),
):
    try:
        contents = await file.read()

        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            raise HTTPException(status_code=400, detail="Invalid image")

        # ZXing espera imagem em grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        results = zxingcpp.read_barcodes(gray)

        if not results:
            return {
                "success": False,
                "content": ""
            }

        return {
            "success": True,
            "content": results[0].text
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
