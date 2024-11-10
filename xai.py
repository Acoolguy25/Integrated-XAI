import requests
import sys
import os
import zlib
import json
import time
import inquirer
import pathlib
from prompt_toolkit import prompt

import modules.path as path
import modules.messages as messages
import modules.text as text

build_path = pathlib.Path(__file__).resolve().parent
url = 'https://api.x.ai/v1/chat/completions'
apiKey = None
model = "grok-beta"
filePath = build_path.as_posix() + "/messages/" + "{file_name}.zlib"

# Global conversation history (this will accumulate the chat)
conversation_history = [
    {
        'role': 'system',
        'content': 'You are a storyteller.'  # System message to set the context
    }
]

conversation_id = "<undefined>"
loaded_chat_name = "<undefined>"

def set_chat_to_conversation_id(name):
    global conversation_id, conversation_history, filePath, loaded_chat_name
    filePath_real = filePath.format(file_name = name)
    if (not os.path.exists(filePath_real)):
        print(f"Not loading chat history: path not found for {name}: {filePath_real}")
        return
    f = open(filePath_real, "rb")
    if (f.readable()):
        content = f.read()
        content = zlib.decompress(content).decode('utf-8')
        conversation_history = json.loads(content)
        id_prop = conversation_history.pop(0)
        conversation_id = id_prop[1]
        loaded_chat_name = name
        for num, val in enumerate(conversation_history):
            if (num > 0):
                processor = text.RichTextProcessor()
                messages.addPersonPreface(val["role"] == "system" or val["role"] == "assistant")
                processor.add_text(val["content"])
                processor.display_lines()
                sys.stdout.write("\n")

        print(f"✅ Loaded {name}.zlib sucessfully!")
        #conversation_history = conversation_history[:50]
    else:
        print("Unable To SET CONVERSATION ID, Read Open Error!")

def save_chat_history():
    global conversation_id, conversation_history, loaded_chat_name
    f = open(filePath.format(file_name = loaded_chat_name), "wb")
    conversation_history.insert(0, ["conversation_id", conversation_id])
    strJson = json.dumps(conversation_history)
    strCompressed = zlib.compress(bytes(strJson, 'utf-8'))
    f.write(strCompressed)
    f.close()
    conversation_history.pop(0)


# Function to send a message to the API with streaming enabled
def send_message_to_api_with_stream():
    global conversation_id, conversation_history
    # Add the user's message to the conversation history


    request_data = {
        'messages': conversation_history,  # The full conversation history
        'model': model,  # The model you're using
        'stream': True,        # Enable streaming for the response
        'temperature': 0.7,    # Control randomness in the response (optional)
        'id': conversation_id=="<undefined>" and None or conversation_id,
        'user': "Ryan"
    }

    processor = text.RichTextProcessor()

    completeReason = "Unknown"
    # Send a POST request with stream enabled
    try:
        response = requests.post(
            url,
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {apiKey}'
            },
            json=request_data,
            stream=True  # Enable streaming
        )

        if response.status_code != 200:
            print("Error: Unable to connect to the API.")
            return

        messages.addPersonPreface(True)
        result = ''  # To accumulate the incoming data as it arrives

        # Process the stream chunk by chunk
        for chunk in response.iter_content(chunk_size=sys.maxsize):
            if chunk:
                # Decode the chunk and append to result
                jsonData = chunk.decode('utf-8').replace('data: ', '').strip().replace('\n\n[DONE]', '')
                # Split the data by double newlines
                json_strings = jsonData.strip().split('\n\n')

                # Decode each JSON object individually
                try:
                    decoded_data = [json.loads(json_str) for json_str in json_strings]
                    for decoded_chunk in decoded_data:
                        conversation_id = decoded_chunk["id"]
                        if (decoded_chunk["object"] == "chat.completion.chunk"):
                            # print(decoded_chunk)
                            for message in decoded_chunk["choices"]:
                                messageContent = message["delta"]
                                if ("finish_reason" in message):
                                    completeReason = message["finish_reason"]
                                elif ("content" in messageContent):
                                    messageText = messageContent["content"]
                                    # sys.stdout.write(messageText)  # Print each chunk as it arrives
                                    processor.add_text(messageText)
                                    processor.display_lines()
                                    # addText(messageText)
                                    result += messageText
                        if (completeReason != "Unknown"):
                            sys.stdout.write("\n")
                            if (completeReason != "stop"):
                                #sys.stdout.write("Stopped: Normally")
                            #else:
                                sys.stdout.write("Stopped: Abornmally",completeReason)
                                sys.stdout.write("\n")
                            break
                except Exception as e:
                    sys.stdout.write("Stopped: Abornmally",e)

        # Add the assistant's response to the conversation history
        conversation_history.append({
            'role': 'assistant',
            'content': result.strip()
        })

    except requests.RequestException as e:
        print('Error during fetch:', e)

# Function to continue the chat
def continue_chat():
    global conversation_history
    while True:
        messages.addPersonPreface(False)
        user_message = prompt("")

        # Exit if the user enters an empty message
        if not user_message.strip():
            break
        elif user_message.startswith("/"):
            if (user_message == "/redo"):
                if (conversation_id != "<undefined>"):
                    conversation_history.pop(-1)
                    send_message_to_api_with_stream()
                else:
                    print("Cannot Redo: No Loaded Chat!")
            else:
                print("Unknown Command!")
        else:
            conversation_history.append({
                'role': 'user',
                'content': user_message
            })
            send_message_to_api_with_stream()

        save_chat_history()

messages.createMessages(build_path)
apiKey = path.yieldGetPath(build_path)
while True:
    answer = inquirer.prompt([
        inquirer.List('starter',
                    message="Please Select",
                    choices=['New Chat', 'Load Most Recent', 'Saved Chats', 'Set API Key', 'Help', 'Quit'],
                ),
    ])["starter"]
    if (answer == 'New Chat'):
        while True:
            loaded_chat_name = input("Name your chat: ")
            if (loaded_chat_name.strip()):
                loaded_chat_name = loaded_chat_name.replace(" ", "_")
                if (build_path / "messages" / (loaded_chat_name + ".zlib")).exists():
                    print("This chat already exists! Please pick a new name.")
                elif not messages.is_valid_filename(filePath.format(file_name=loaded_chat_name) + ".zlib"):
                    print(f"The name \"{loaded_chat_name}\" contains invalid character(s)!")
                else:
                    continue_chat()
                    break
            else:
                break
    elif (answer == 'Load Most Recent'):
        most_recent = messages.get_latest_message(build_path / "messages")
        if (not most_recent):
            print("No loaded messages found! Please create a new chat!")
            continue
        set_chat_to_conversation_id(most_recent.stem)
        continue_chat()
    elif (answer == 'Saved Chats'):
        messageNames = messages.get_all_messages(build_path / "messages")
        if messageNames.count() == 0:
            print("❌ No Saved Messages found! Please create your own!")
        messageNames.append("Back")
        answer = inquirer.prompt([
            inquirer.List('starter',
                        message="Please Select",
                        choices=messageNames,
                    ),
        ])["starter"]
        if answer == "Back":
            continue
        real_name = answer.replace(" ", "_")
        set_chat_to_conversation_id(real_name)
        continue_chat()
    elif (answer == 'Help'):
        print("Visit the GitHub repository in order to get your API_Key")
        time.sleep(1)
    elif (answer == 'Set API Key'):
        apiKey = path.yieldGetPath(apiKey)
    elif (answer == 'Quit'):
        break
    else:
        break