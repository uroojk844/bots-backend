from fastapi import FastAPI
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# 1. Define the allowed origins (websites) that can connect to your API
origins = ["*"]

# 2. Add the CORS middleware to your application
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],  # Allows requests from specific domains
    allow_credentials=True,  # Allows cookies and authentication
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, PUT,
    allow_headers=["*"],  # Allows all HTTP headers
)

from my import get_info_basic


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
