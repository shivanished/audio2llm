# main.py (python example)

import os
import requests
import json
import re

from deepgram import (
    DeepgramClient,
    PrerecordedOptions,
    FileSource,
)


def transcribe_file(AUDIO_FILE):
    try:
        # STEP 1 Create a Deepgram client using the API key
        deepgram = DeepgramClient("eb4a2c767aec1474b4887a68ba1659a8d2476364")

        with open(AUDIO_FILE, "rb") as file:
            buffer_data = file.read()

        payload: FileSource = {
            "buffer": buffer_data,
        }

        #STEP 2: Configure Deepgram options for audio analysis
        options = PrerecordedOptions(
            model="nova-2",
            smart_format=True,
            diarize=True
        )

        # STEP 3: Call the transcribe_file method with the text payload and options
        response = deepgram.listen.prerecorded.v("1").transcribe_file(payload, options)

        # STEP 4: Print the response
        output_file = re.sub(r'\.mp3$', '.jsonl', AUDIO_FILE)
        process_transcription(response, output_file)

    except Exception as e:
        print(f"Exception: {e}")



def process_transcription(response, output_file):
    labels_one = generate_labels(response, "Speaker 0", "Speaker 1")
    labels_two = generate_labels(response, "Speaker 1", "Speaker 0")

    jsonl_data = accurate_labeling(labels_one, labels_two)

    with open(output_file, 'w') as f:
        for entry in jsonl_data:
            f.write(entry + "\n")

    # with open(output_file, 'w') as f:
    #     json.dump(jsonl_data, f, indent=4)

def generate_labels(response, user_label, assistant_label):
    jsonl_data = []
    transcript = response['results']['channels'][0]['alternatives'][0]['paragraphs']['transcript'].split("\n\n")
    json_prompt = ""
    json_completion = ""

    for paragraph in transcript:
        text = paragraph.replace(user_label, "User").replace(assistant_label, "Assistant")
        split_text = text.split(": ", 1)
        role, content = split_text[0], split_text[1] if len(split_text) > 1 else ""

        if role == "User":
            if json_completion:  # Handles case where Assistant dialogue precedes User dialogue at the start
                jsonl_data.append(json.dumps({
                    "prompt": json_prompt,
                    "completion": json_completion
                }))
                json_completion = ""  # Reset completion for next dialogue pair
            json_prompt = f"User: {strip_whitespace(content)}"
        elif role == "Assistant":
            json_completion = f"Assistant: {strip_whitespace(content)}"
            if json_prompt and json_completion:
                jsonl_data.append(json.dumps({
                    "prompt": json_prompt,
                    "completion": json_completion
                }))
                # Reset for next dialogue pair
                json_prompt = ""
                json_completion = ""

    # This handles any remaining dialogues where a prompt doesn't immediately follow its completion
    if json_prompt and json_completion:
        jsonl_data.append(json.dumps({
            "prompt": json_prompt,
            "completion": json_completion
        }))

    return jsonl_data


def accurate_labeling(labels_one, labels_two):
    labels_one_valid = False
    labels_two_valid = False
    

    for entry in labels_one:
        try:
            entry_dict = json.loads(entry)
        except json.JSONDecodeError as e:
            print(f"Failed to decode JSON: {e}")
        except KeyError as e:
            print(f"Key not found: {e}")
            
        if contains_six_digit_number(entry_dict['prompt']):
            labels_one_valid = True

    for entry in labels_two:
        try:
            entry_dict = json.loads(entry)
        except json.JSONDecodeError as e:
            print(f"Failed to decode JSON: {e}")
        except KeyError as e:
            print(f"Key not found: {e}")

        if contains_six_digit_number(entry_dict['prompt']):
            labels_two_valid = True

    return labels_one if labels_one_valid else labels_two

def strip_whitespace(input_string):
    return re.sub(r'[^\S ]+', '', input_string)

def contains_six_digit_number(s):
    return bool(re.search(r'\b\d{6}\b', s))



transcribe_file("call-1.mp3")
transcribe_file("call-2.mp3")
