from openai import OpenAI
import json


# ---------------------------------------------------
# OpenRouter Client
# ---------------------------------------------------

client = OpenAI(
    base_url="https://openrouter.ai/api/v1"
)


# ---------------------------------------------------
# AI Schema Generator
# ---------------------------------------------------

def generate_schema(prompt):

    full_prompt = f"""
    You are an ERP schema architect.

    Analyze this prompt:

    "{prompt}"

    Return ONLY valid JSON.

    Example:

    {{
      "fields": [
        {{
          "label": "Employee Name",
          "fieldtype": "Data"
        }}
      ]
    }}

    Allowed fieldtypes:

    Data
    Currency
    Date
    Link
    Select
    Attach
    Check
    Small Text
    Int
    Table

    Infer intelligently.
    """

    response = client.chat.completions.create(

        model="openai/gpt-3.5-turbo",

        messages=[
            {
                "role": "user",
                "content": full_prompt
            }
        ]
    )

    text = response.choices[0].message.content.strip()

    # ---------------------------------------------------
    # Remove Markdown Wrappers
    # ---------------------------------------------------

    text = text.replace("```json", "")
    text = text.replace("```", "")

    data = json.loads(text)

    return data
