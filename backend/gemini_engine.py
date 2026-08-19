import google.generativeai as genai
from config import GEMINI_API_KEY

genai.configure(
    api_key=GEMINI_API_KEY
)

model = genai.GenerativeModel(
    "models/gemini-flash-latest"
)

def generate_explanation(prompt):

    response = model.generate_content(
        prompt
    )

    return response.text