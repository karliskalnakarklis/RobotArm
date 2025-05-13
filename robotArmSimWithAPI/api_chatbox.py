import requests
import uuid

# Configuration
HA_URL = "https://tfd9eaklrsaswbraeoswnlyfx4pmaaoj.ui.nabu.casa"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJjYzIxZDIyZDdjZmE0MGQ1YTIxMjYyOWMwNDIyNzJlYSIsImlhdCI6MTc0NjcwNTMyMSwiZXhwIjoyMDYyMDY1MzIxfQ.UI0lzY2hLPEFmWQaHkvjw-VGwLzie_-PXNA2PMIPvws"
AGENT_ID = "conversation.llama3_2_2"

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
}

# Endpoint for conversation processing
ENDPOINT = "/api/conversation/process"

def converse(text: str, conversation_id: str = None) -> dict:
    """
    Send a text input to Home Assistant conversation API and return the JSON response.

    :param text: Text command to send.
    :param conversation_id: Optional UUID for multi-turn context.
    :return: Parsed JSON or raises HTTPError.
    """
    url = f"{HA_URL}{ENDPOINT}"
    payload = {
        "text": text,
        "agent_id": AGENT_ID,
    }
    if conversation_id:
        payload["conversation_id"] = conversation_id

    print(f"\n➡️ POST {url}")
    print("📝 Payload:", payload)

    response = requests.post(url, headers=HEADERS, json=payload)
    try:
        response.raise_for_status()
    except requests.HTTPError as e:
        print(f"❌ Error {response.status_code}: {response.text}")
        raise

    return response.json()

if __name__ == "__main__":
    print("🗣️ Starting chat with Home Assistant agent 'llama3.2'. Type 'exit' to quit.")
    conv_id = None
    while True:
        user_input = input("You: ")
        if user_input.strip().lower() in ("exit", "quit"):
            print("👋 Goodbye!")
            break
        try:
            result = converse(user_input, conversation_id=conv_id)
        except Exception:
            print("⚠️ Failed to get a valid response. Check the error above.")
            continue
        # Update conversation ID if returned
        conv_id = result.get("conversation_id", conv_id)
        # Extract assistant reply
        reply = result.get("response") or result.get("result") or "<no response>"
        print(f"Assistant: {reply}")