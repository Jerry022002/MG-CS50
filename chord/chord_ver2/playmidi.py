import requests

API_KEY = "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"
API_URL = "https://musescore-openai.herokuapp.com/"

chord_progression = ['Cmaj7', 'Am7', 'D7', 'Gmaj7']  # Example chord progression

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

data = {
    "chords": chord_progression,
    "tempo": 120,  # Adjust as needed
    "length": 64,  # Number of musical steps to generate
}

response = requests.post(API_URL + "generate", json=data, headers=headers)

if response.status_code == 200:
    generated_music = response.json()["music"]
    # Process and play the generated_music
else:
    print("API request failed:", response.status_code, response.text)
