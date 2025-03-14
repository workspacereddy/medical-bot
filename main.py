from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import requests

# Initialize the FastAPI app
app = FastAPI()

# CORS Middleware configuration (Allow all origins, you can customize this for your frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can replace "*" with specific domains like "https://your-frontend.vercel.app"
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Define the input data model (Request body)
class ChatRequest(BaseModel):
    input_text: str

# Function to infer the role based on keywords in the input text
def infer_role(text: str):
    # Define basic keywords for detecting roles
    health_keywords = ["feel", "sick", "ill", "pain", "headache", "fever", "cough", "nausea"]
    advice_keywords = ["what", "how", "should", "do", "help", "advice", "recommend"]
    
    # Check if the input contains health-related keywords
    if any(keyword in text.lower() for keyword in health_keywords):
        return "doctor"
    
    # Check if the input contains advice-related keywords
    elif any(keyword in text.lower() for keyword in advice_keywords):
        return "advisor"
    
    # Default to "advisor" if no clear role is identified
    return "advisor"

# Define an endpoint for the chat API
@app.post("/api/chat")
async def chat(request: ChatRequest):
    input_text = request.input_text
    
    # Infer the role based on the input text
    role = infer_role(input_text)
    
    # Construct the prompt for Hugging Face API
    prompt = f"Act as a {role}. {input_text}"

    # Hugging Face API URL for the model
    url = "https://api-inference.huggingface.co/models/meta-llama/Llama-3.2-3B-Instruct"
    
    # Hugging Face API key (replace with your actual key)
    headers = {
        "Authorization": "Bearer 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"
    }

    # Send the request to Hugging Face's API
    response = requests.post(
        url,
        headers=headers,
        json={"inputs": prompt}
    )

    # Check if the request was successful (status code 200)
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Error with the model request.")

    # Parse the response from the model
    try:
        result = response.json()
        generated_text = result[0].get("generated_text", "Sorry, I couldn't generate a response.")
        return {"response": generated_text}
    except ValueError:
        raise HTTPException(status_code=500, detail="Error: Could not parse the response!")

