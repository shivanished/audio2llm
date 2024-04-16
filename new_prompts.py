import json
from openai import OpenAI

client = OpenAI(api_key='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')


def load_jsonl_data(file_path):
    with open(file_path, 'r') as file:
        return [json.loads(line.strip()) for line in file]


def generate_new_prompts(*file_paths):
    messages = [{
        "role": "system", 
        "content": "Given the conversation snippet between a user and an assistant, create one detailed prompt that defines the behavior or the personality of the assistant we are trying to clone."
    }]
    
    for file_path in file_paths:
        transcripts = load_jsonl_data(file_path)
        messages.extend(create_messages(transcripts))
        
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages
    )

    # Assuming response is a Pydantic model, convert to dict for JSON serialization
    response_dict = response.dict() if hasattr(response, 'dict') else response

    print(response_dict['choices'][0]['message']['content'])
    # with open('combined_response.json', 'w') as f:
    #     json.dump(response_dict, f, ensure_ascii=False, indent=4)


def create_messages(transcripts):
    messages = []
    for transcript in transcripts:
        if 'prompt' in transcript and 'completion' in transcript:
            # Extract user content
            if ": " in transcript['prompt']:
                user_content = transcript['prompt'].split(": ", 1)[1]
                messages.append({
                    "role": "user",
                    "content": user_content
                })
            
            # Extract assistant content
            if ": " in transcript['completion']:
                assistant_content = transcript['completion'].split(": ", 1)[1]
                messages.append({
                    "role": "assistant",
                    "content": assistant_content
                })
    return messages

generate_new_prompts("call-1.jsonl", "call-2.jsonl")