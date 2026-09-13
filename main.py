import importlib
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
from my import get_info_basic


@app.get("/customers")
async def list_customers():
    customers_dir = os.path.join(os.path.dirname(__file__), "customers")
    customers = []
    for entry in sorted(os.scandir(customers_dir), key=lambda e: e.name):
        if entry.is_dir() and not entry.name.startswith("_"):
            module = importlib.import_module(f"customers.{entry.name}.about")
            customers.append({"id": entry.name, "name": module.name})
    return customers


@app.get("/chat")
async def read_root(company_id: str, query: str):
    return StreamingResponse(get_info_basic(query, company_id), media_type="text/plain")


@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <!DOCTYPE html>
<html>
<head>
    <title>AI Voice</title>
</head>

<body>

<h2>AI Voice Chat</h2>

<input id="company" value="proficio">
<input id="query" value="Tell me about this company">

<button onclick="sendMessage()">Send</button>

<div id="output"></div>

<script>

async function sendMessage() {

    const companyId = document.getElementById("company").value;
    const query = document.getElementById("query").value;
    const output = document.getElementById("output");

    output.textContent = "";

    const response = await fetch(
        `/chat?company_id=${encodeURIComponent(companyId)}&query=${encodeURIComponent(query)}`
    );

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    let sentenceBuffer = "";

    while (true) {

        const { value, done } = await reader.read();

        if (done) break;

        const text = decoder.decode(value, { stream: true });

        output.textContent += text;

        sentenceBuffer += text;

        // Speak when we have a complete sentence
        const sentences = sentenceBuffer.match(/[^.!?]+[.!?]+/g);

        if (sentences) {

            for (const sentence of sentences) {
                //speak(sentence);
            }

            sentenceBuffer = sentenceBuffer.replace(
                /[^.!?]+[.!?]+/g,
                ""
            );
        }
    }

    // Speak remaining text
    if (sentenceBuffer.trim()) {
        //speak(sentenceBuffer);
    }
}


function speak(text) {

    const utterance = new SpeechSynthesisUtterance(text);

    utterance.rate = 1.0;
    utterance.pitch = 1.0;

    window.speechSynthesis.speak(utterance);
}

</script>

</body>
</html>
    """
