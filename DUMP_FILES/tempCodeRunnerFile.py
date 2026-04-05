from openai import OpenAI 
client = OpenAI()

result = client.responses.create(
    model="gpt-5.4",
    input="Write a short bedtime story for children."
)
print(result.output_text)