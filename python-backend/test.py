from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv(override=True)

print("API KEY exists:", bool(os.environ.get("OPENAI_API_KEY")))
client = OpenAI(
    api_key=os.environ["OPENAI_API_KEY"]
)

response = client.chat.completions.create(
    model="gpt-6-luna",
    messages=[
        {"role": "user", "content": "Hello, API test"}
    ],
)

print(response.choices[0].message.content)