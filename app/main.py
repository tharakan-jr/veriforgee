from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(title="VeriForge", version="0.1.0")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!doctype html>
    <html><head><title>VeriForge</title></head>
    <body style='font-family:system-ui;max-width:900px;margin:60px auto;padding:20px'>
      <h1>VeriForge</h1>
      <p>Paste AI-generated code → Review → Explain → Ground → Fix → Verify.</p>
      <p>Backend is running. Replace this page with the team UI.</p>
    </body></html>
    """
