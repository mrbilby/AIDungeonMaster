import openai
import os
import time
import tkinter as tk
from tkinter import ttk
import threading

# Set your OpenAI API key here
os.environ['OPENAI_API_KEY'] = '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'
client = openai.OpenAI() 

model = "gpt-3.5-turbo-16k"  # Specify the model you wish to use

def create_dungeon_master_assistant():
    try:
        # Check if the Dungeon Master assistant ID file exists
        with open('dungeon_master_assistant_id.txt', 'r') as file:
            assistant_id = file.read().strip()
            print(f"Dungeon Master Assistant ID already exists: {assistant_id}")
            return assistant_id
    except FileNotFoundError:
        # If the file does not exist, create a new Dungeon Master assistant
        dungeonMasterAssistant = client.beta.assistants.create(
            name="DungeonMaster",
            instructions="""
            Act as a dungeon master in a fantasy role-playing game. Guide players through an engaging story 
            within a medieval setting, using formal, descriptive language. Respond to player actions with detailed 
            narrative developments and clear outcomes, while maintaining a balance between challenge and enjoyment. 
            Avoid explicit content and ensure the game remains suitable for all audiences. Adapt the story based on 
            player decisions, ensuring to keep them engaged with creative descriptions, unexpected plot twists, and 
            relevant character interactions. Resolve any ambiguities in player actions by asking clarifying questions 
            and offer hints if players seem stuck. Your primary goal is to ensure an immersive, enjoyable, and 
            seamless gaming experience.
            """,
            model=model
        )
        assistant_id = dungeonMasterAssistant.id
        # Save the new assistant ID to a file
        with open('dungeon_master_assistant_id.txt', 'w') as file:
            file.write(assistant_id)
        print(f"New Dungeon Master Assistant ID created: {assistant_id}")
        return assistant_id

def create_thread():
    thread = client.beta.threads.create()
    thread_id = thread.id
    return thread_id

def submit_user_message(thread_id, user_message):
    client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=user_message
    )

def save_thread():
    with open('thread_id.txt', 'w') as file:
        file.write(thread_id)
    print("Thread saved successfully.")
    with open('companion_thread_id.txt', 'w') as file:
        file.write(companion_thread_id)
    print("Companion thread saved successfully.")

def load_thread():
    global thread_id  # Important: Update the global variable
    try:
        with open('thread_id.txt', 'r') as file:
            thread_id = file.read().strip()
        with open('companion_thread_id.txt', 'r') as file:
            companion_thread_id = file.read().strip()            
        print(f"Thread loaded successfully: {thread_id}")
        print(f"Companion thread loaded successfully: {companion_thread_id}")

        # Clear previous history in the GUI
        history_box.delete("1.0", "end")  
        # Fetch the messages from the loaded thread
        messages = client.beta.threads.messages.list(thread_id=thread_id, order="asc")
        # Display each message in the history box
        for message in messages.data:
            message_text = message.content[0].text.value
            display_text = f"{message.role.capitalize()}: {message_text}\n"
            history_box.insert("end", display_text)
    except FileNotFoundError:
        print("No thread save file found.")

def callDungeonMaster():
    def background_task():
        print("Background task started")  # Debug print
        user_message = description_entry.get("1.0", "end-1c").strip()
        print(f"User message: {user_message}")  # Debug print
        if user_message:
            submit_user_message(thread_id, user_message)
            run = client.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=dungeon_master_assistant_id
            )
            print(f"Run created: {run.id}")  # Debug print
            
            # Loop to check the run's status
            while True:
                run_updated = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
                print(f"Run status: {run_updated.status}")  # Debug print
                if run_updated.status == "completed":
                    break  # Exit the loop if run is completed
                time.sleep(5)  # Wait for a few seconds before checking again
            
            # Once completed, retrieve and display the messages
            messages = client.beta.threads.messages.list(thread_id=thread_id, order="asc")
            print("Messages retrieved")  # Debug print
            root.after(0, lambda: update_output(messages))

    def update_output(messages):
        output_box.delete("1.0", "end")
        description_entry.delete("1.0", "end")
        for message in messages.data:
            message_text = message.content[0].text.value
            display_text = f"{message.role.capitalize()}: {message_text}\n"
            print(f"Display text: {display_text}")  # Debug print
            history_box.insert("end", display_text)
            if message.role != "user":
                output_box.insert("end", display_text)

    threading.Thread(target=background_task).start()




def create_adventure_companion():
    try:
        # Check if the Adventure Companion assistant ID file exists
        with open('adventure_companion_id.txt', 'r') as file:
            companion_id = file.read().strip()
            print(f"Adventure Companion ID already exists: {companion_id}")
            return companion_id
    except FileNotFoundError:
        # If the file does not exist, create a new Adventure Companion assistant
        companionAssistant = client.beta.assistants.create(
            name="AdventureCompanion",
            instructions="""
            Act as a fun and charming rogue companion in a fantasy role-playing game. Engage the player 
            with witty banter, clever insights, and humorous asides. Provide helpful advice and encouragement 
            on the journey, making the adventure more enjoyable and entertaining. Be ready to discuss strategies, 
            lore, and tactics while keeping a light-hearted and adventurous spirit.
            """,
            model=model
        )
        companion_id = companionAssistant.id
        # Save the new assistant ID to a file
        with open('adventure_companion_id.txt', 'w') as file:
            file.write(companion_id)
        print(f"New Adventure Companion ID created: {companion_id}")
        return companion_id
    
def chatCompanion():
    def background_task():
        print("Background task started for companion")  # Debug print
        user_message = compChat_entry.get("1.0", "end-1c").strip()
        print(f"Companion user message: {user_message}")  # Debug print
        if user_message:
            dm_messages = client.beta.threads.messages.list(thread_id=thread_id, order="desc", limit=1)
            latest_dm_response = dm_messages.data[0].content[0].text.value if dm_messages.data else "No recent dungeon master response."
            print(f"Latest DM response: {latest_dm_response}")  # Debug print
            combined_message = f"DM: {latest_dm_response}\nYou: {user_message}"
            submit_user_message(companion_thread_id, combined_message)
            run = client.beta.threads.runs.create(
                thread_id=companion_thread_id,
                assistant_id=adventure_companion_id
            )
            print(f"Companion run created: {run.id}")  # Debug print

            # Loop to check the run's status
            while True:
                run_updated = client.beta.threads.runs.retrieve(thread_id=companion_thread_id, run_id=run.id)
                print(f"Companion run status: {run_updated.status}")  # Debug print
                if run_updated.status == "completed":
                    break  # Exit the loop if run is completed
                time.sleep(5)  # Wait for a few seconds before checking again

            # Once completed, retrieve and display the messages
            messages = client.beta.threads.messages.list(thread_id=companion_thread_id, order="asc")
            print("Companion messages retrieved")  # Debug print
            root.after(0, lambda: update_companion_output(messages))

    def update_companion_output(messages):
        print("Updating companion output")  # Debug print
        chat_output_box.delete("1.0", "end")
        compChat_entry.delete("1.0", "end")
        for message in messages.data:
            message_text = message.content[0].text.value
            display_text = f"{message.role.capitalize()}: {message_text}\n"
            print(f"Companion display text: {display_text}")  # Debug print
            if message.role == "assistant":
                chat_output_box.insert("end", display_text)
                history_box.insert("end", display_text)

    threading.Thread(target=background_task).start()




# Main script execution
dungeon_master_assistant_id = create_dungeon_master_assistant()
print(dungeon_master_assistant_id)

adventure_companion_id = create_adventure_companion()
print(adventure_companion_id)

thread_id = create_thread()
companion_thread_id = create_thread()  # Create a separate thread for the companion conversation

root = tk.Tk()
root.title("AI Dungeon Master")
root.geometry('1400x700')  # Adjust overall window size if needed

# Positioning text boxes for description, materials, and other information
description_label = tk.Label(root, text="Your choice")
description_label.place(relx=0.01, rely=0.01)
description_entry = tk.Text(root, height=5, width=55)
description_entry.place(relx=0.01, rely=0.05)

# Classify button, positioned below the text boxes
classify_btn = tk.Button(root, text="Input data", padx=10, pady=5, fg="black", bg="#263D42", command=callDungeonMaster)
classify_btn.place(relx=0.01, rely=0.2)
classify_btn.config(command=callDungeonMaster)

# Output box for displaying the latest API response, positioned accordingly
output_label = tk.Label(root, text="Latest Output")
output_label.place(relx=0.01, rely=0.3)
output_box = tk.Text(root, height=30, width=55)  # Adjust size as needed
output_box.place(relx=0.01, rely=0.34)

# Positioning text boxes for description, materials, and other information
compChat_label = tk.Label(root, text="Chat with companion")
compChat_label.place(relx=0.35, rely=0.01)
compChat_entry = tk.Text(root, height=5, width=55)
compChat_entry.place(relx=0.35, rely=0.05)

# Classify button, positioned below the text boxes
chat_btn = tk.Button(root, text="Input chat", padx=10, pady=5, fg="black", bg="#263D42", command=chatCompanion)
chat_btn.place(relx=0.35, rely=0.2)
chat_btn.config(command=chatCompanion)

# Output box for displaying the latest API response, positioned accordingly
chat_output_label = tk.Label(root, text="Latest chat")
chat_output_label.place(relx=0.35, rely=0.3)
chat_output_box = tk.Text(root, height=30, width=55)  # Adjust size as needed
chat_output_box.place(relx=0.35, rely=0.34)

# History box for displaying all messages so far, positioned to the right
history_label = tk.Label(root, text="Conversation History")
history_label.place(relx=0.7, rely=0.01)  # Adjust position as needed
history_box = tk.Text(root, height=45, width=55)  # Adjust size as needed
history_box.place(relx=0.7, rely=0.05)  # Adjust position as needed

# Save Thread button
save_thread_btn = tk.Button(root, text="Save Thread", padx=10, pady=5, fg="black", bg="#263D42", command=save_thread)
save_thread_btn.place(relx=0.01, rely=0.91)

# Load Thread button
load_thread_btn = tk.Button(root, text="Load Thread", padx=10, pady=5, fg="black", bg="#263D42", command=load_thread)
load_thread_btn.place(relx=0.15, rely=0.91)


root.mainloop()