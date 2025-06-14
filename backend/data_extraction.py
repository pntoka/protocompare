import json
import openai
from openai import OpenAI
import re

API_KEY = ""
# Static system prompt for consistent instructions
SYSTEM_PROMPT = """
You are a helpful scientific protocol information extractor. 

Given a protocol step, extract its structured elements into JSON based on the template provided below. There might be mltiple steps in the protocol, therefore you should return a list of JSON objects, each representing a step in the protocol.

Use this following schema for each step exactly:
{
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["step_number", "step_type", "input", "output", "action", "parameter"],
    "properties": {
      "step_number": {
        "type": "integer",
        "description": "The sequential number of the step in the procedure"
      },
      "step_type": {
        "type": "string",
        "description": "Type of the step, e.g., filtration, centrifugation, heating"
      },
      "input": {
        "type": "string",
        "description": "Materials or substances used in this step"
      },
      "output": {
        "type": "string",
        "description": "Result or product obtained from this step"
      },
      "action": {
        "type": "string",
        "description": "The core operation performed, e.g., heat, filter, mix"
      },
      "parameter": {
        "type": "object",
        "description": "Key-value pairs describing step-specific parameters",
        "additionalProperties": {
          "type": ["string", "number", "boolean"]
        }
      }
    }
  }
Only return the JSON. No explanations.
"""

SYSTEM_PROMPT_2 = """"

You are a helpful scientific protocol procedure formatter.

Given a list of protocol steps in the provided JSON schema, format them into a human-readable procedure. Each step should be presented in a clear and concise manner, maintaining the order of the steps.

Here is the schema that is used for the provided steps:

{
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["step_number", "step_type", "input", "output", "action", "parameter"],
    "properties": {
      "step_number": {
        "type": "integer",
        "description": "The sequential number of the step in the procedure"
      },
      "step_type": {
        "type": "string",
        "description": "Type of the step, e.g., filtration, centrifugation, heating"
      },
      "input": {
        "type": "string",
        "description": "Materials or substances used in this step"
      },
      "output": {
        "type": "string",
        "description": "Result or product obtained from this step"
      },
      "action": {
        "type": "string",
        "description": "The core operation performed, e.g., heat, filter, mix"
      },
      "parameter": {
        "type": "object",
        "description": "Key-value pairs describing step-specific parameters",
        "additionalProperties": {
          "type": ["string", "number", "boolean"]
        }
      }
    }
  }

Format the procdure into a human-readable format, taking care to maintain the order of the steps. Use clear and concise language, and ensure that each step is easy to understand. Only return the formatted procedure text, without any additional explanations or comments.
"""

openai.api_key = API_KEY

# user_prompt =  "CQDs were synthesized by the usage of O. basilicum L. extract via a simple hydrothermal method (Fig. 1). In a typical one-step synthesizing procedure, 2.0 g of O. basilicum L. seed was added to 100 mL of distilled water and stirred at 50 °C for 2 h. Then, the obtained extract was filtered and transferred into a 100 mL Teflon-lined stainless-steel autoclave to be heated at 180 °C for 4 h. Once the autoclave was cooled naturally at room temperature and the solution was centrifuged (12,000 rpm) for 15 min, the prepared brown solution was filtered through a fine-grained 0.45 μm membrane to remove larger particles. Finally, the solution was freeze-dried to attain the dark brown powder of CQDs." 


def extract_json_from_response(response_text):
    # Remove markdown code block wrappers like ```json ... ```
    json_match = re.search(r"```json\s*(\[\s*{.*}\s*\])\s*```", response_text, re.DOTALL)
    if json_match:
        json_str = json_match.group(1)
        return json.loads(json_str)
    else:
        # If no code block found, try parsing whole text directly
        return json.loads(response_text)
    
def extract_protocol(user_prompt):
    # Load OpenAI API key
    
    client = OpenAI(api_key=API_KEY)

    # Load protocol steps from the input JSON
    

    # output = []

    try:
        res = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0
        )
        response_content = res.choices[0].message.content
        # print("Response from OpenAI:", response_content)
        parsed_json = extract_json_from_response(response_content)
        # output.append(parsed_json)

    except Exception as e:
        print(f"Error processing step: {e}")

    return parsed_json
    # Save the result
    # with open("output_extracted.json", "w") as out_file:
    #     json.dump(output, out_file, indent=2)

    # print("Extraction complete. Output saved to output_extracted.json")

# extract_protocol(user_prompt)

def make_pretty_procedure(input_json_protocol):
    client = OpenAI(api_key=API_KEY)
    try:
        res = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT_2},
                {"role": "user", "content": json.dumps(input_json_protocol, indent=2)}
            ],
            temperature=0
        )
        response_content = res.choices[0].message.content
        return response_content.strip()
    except Exception as e:
        print(f"Error formatting procedure: {e}")
        return None