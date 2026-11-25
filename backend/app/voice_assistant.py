"""
MediVoice AI - Voice Assistant
Handles real-time voice interaction for doctor appointment booking.
"""

class MediVoiceAssistant:
    def __init__(self):
        self.is_running = False
        self.conversation_history = []

    async def start(self):
        self.is_running = True
        print("MediVoice AI voice assistant started.")

    async def stop(self):
        self.is_running = False
        print("MediVoice AI voice assistant stopped.")

    def add_message(self, role, content):
        self.conversation_history.append({
            "role": role,
            "content": content
        })

    def get_history(self):
        return self.conversation_history