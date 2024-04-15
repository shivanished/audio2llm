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
        output_file = re.sub(r'\.mp3$', '.json', AUDIO_FILE)
        process_transcription(response, output_file)

    except Exception as e:
        print(f"Exception: {e}")



def process_transcription(response, output_file):
    jsonl_data = []

    transcript = response['results']['channels'][0]['alternatives'][0]['paragraphs']['transcript'].split("\n\n")

    json_object = {}
    json_prompt = ""
    json_completion = ""

    for paragraph in transcript:
        text = paragraph.replace("Speaker 0", "Assistant").replace("Speaker 1", "User")

        if text.split()[0] == "User:":
            json_prompt = text

        if text.split()[0] == "Assistant:":
            json_completion = text
            if json_prompt is not None and json_completion is not None:
                jsonl_data.append(json.dumps({
                        "prompt": f"{json_prompt}",
                        "completion": f"{json_completion}"
                    }))
                json_prompt = ""
                json_completion = ""

    with open(output_file, 'w') as f:
        for entry in jsonl_data:
            f.write(entry + "\n")

    # with open(output_file, 'w') as f:
    #     json.dump(jsonl_data, f, indent=4)


transcribe_file("call-1.mp3")
transcribe_file("call-2.mp3")
