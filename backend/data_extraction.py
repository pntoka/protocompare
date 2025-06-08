import json
import openai
from openai import OpenAI
import re

API_KEY = ""
# Static system prompt for consistent instructions
SYSTEM_PROMPT = """
You are a helpful scientific protocol information extractor. 

Given a protocol step, extract its structured elements into JSON based on the template provided below. There might be mltiple steps in the protocol, therefore you should return a list of JSON objects, each representing a step in the protocol.

Use this format exactly:
{
  "num": <number of the step in the sequence - int>,
  "type": "<The main verb that describes what is being done to the input (e.g., "stir", "filter", "heat", "centrifuge", "freeze-dry", "wash", "sonicate", etc.). Use lowercase and keep it concise.>",
  "input": "<what is being processed>",
  "output": "<what is the result>",
  "action": "<what action is performed>",
  "parameters": { "param1": "value", ... }
}
Only return the JSON. No explanations.
"""
openai.api_key = API_KEY

user_prompt =  "CQDs were synthesized by the usage of O. basilicum L. extract via a simple hydrothermal method (Fig. 1). In a typical one-step synthesizing procedure, 2.0 g of O. basilicum L. seed was added to 100 mL of distilled water and stirred at 50 °C for 2 h. Then, the obtained extract was filtered and transferred into a 100 mL Teflon-lined stainless-steel autoclave to be heated at 180 °C for 4 h. Once the autoclave was cooled naturally at room temperature and the solution was centrifuged (12,000 rpm) for 15 min, the prepared brown solution was filtered through a fine-grained 0.45 μm membrane to remove larger particles. Finally, the solution was freeze-dried to attain the dark brown powder of CQDs." 


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
    

    output = []

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
        print("Response from OpenAI:", response_content)
        parsed_json = extract_json_from_response(response_content)
        output.append(parsed_json)

    except Exception as e:
        print(f"Error processing step: {e}")

    # Save the result
    with open("output_extracted.json", "w") as out_file:
        json.dump(output, out_file, indent=2)

    print("Extraction complete. Output saved to output_extracted.json")

extract_protocol(user_prompt)
