import websocket
import json
import threading
import time

def on_message(ws, message):
    """
    This function is called whenever a message is received from the WebSocket.
    This is where you can intercept, archive, or search chat messages.
    """
    print("<<< Received Message:")
    try:
        # Pretty-print the JSON message for readability
        parsed_message = json.loads(message)
        print(json.dumps(parsed_message, indent=2))
        
        # TODO: Add your custom logic here
        # - Save the message to a file or database
        # - Search for specific keywords in the message
        # - Trigger alerts based on message content

    except json.JSONDecodeError:
        # If the message is not JSON, print it as plain text
        print(message)

def on_error(ws, error):
    """Called on WebSocket errors."""
    print(f"--- WebSocket Error: {error} ---")

def on_close(ws, close_status_code, close_msg):
    """Called when the WebSocket connection is closed."""
    print(f"--- WebSocket Connection Closed: {close_status_code} {close_msg} ---")

def on_open(ws):
    """Called once the WebSocket connection is established."""
    print("--- WebSocket Connection Opened ---")
    # You could potentially send an initial "hello" or authentication message here if required.

def connect_and_listen(websocket_url, auth_token):
    """
    Connects to the Grindr WebSocket and listens for messages.
    
    Args:
        websocket_url (str): The wss:// URL for the chat server.
        auth_token (str): The authorization token.
    """
    print(f"Attempting to connect to {websocket_url}")
    
    # Set the necessary headers for authentication, similar to your HTTP requests.
    # The exact header name ('Authorization', 'Sec-WebSocket-Protocol', etc.)
    # may vary and should be determined from your intercept logs.
    headers = {
        "Authorization": f"Grindr3 {auth_token}"
    }

    ws = websocket.WebSocketApp(
        websocket_url,
        header=headers,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )

    # Run the WebSocket client in a separate thread to keep it running
    wst = threading.Thread(target=ws.run_forever)
    wst.daemon = True
    wst.start()
    
    print("WebSocket listener started. Press Ctrl+C to exit.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        ws.close()
        print("WebSocket connection closed.")

if __name__ == '__main__':
    # --- IMPORTANT ---
    # You must find the correct WebSocket URL and determine how the auth token is passed.
    # Look in your `GrindrPlus_HttpLogs.txt` for a request with a `wss://` URL.
    
    # These are placeholder values. Replace them with the actual values from your logs.
    # The websocket URL will likely be different.
    WEBSOCKET_URL = "wss://chat-ws.grindr.com/v4/connect" 
    
    # Use the same authToken you get from GrindrAccess_Info.txt
    AUTH_TOKEN = "your_auth_token_here" 

    if AUTH_TOKEN == "your_auth_token_here":
        print("Please replace the placeholder AUTH_TOKEN in this script.")
    else:
        connect_and_listen(WEBSOCKET_URL, AUTH_TOKEN)
