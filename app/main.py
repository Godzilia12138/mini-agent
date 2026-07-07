from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# ========== 1. 解决 CORS ==========
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== 2. Chat接口（修复422核心） ==========
@app.post("/chat")
async def chat(
    message: str = Form(...),
    file: UploadFile = File(None)
):
    file_name = file.filename if file else None

    # 模拟AI回复
    answer = f"收到消息：{message}"
    if file_name:
        answer += f"\n已收到文件：{file_name}"

    return {
        "answer": answer
    }