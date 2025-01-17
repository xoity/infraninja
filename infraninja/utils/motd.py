import random
from datetime import datetime

def show_motd():
    """Display a Message of the Day when infraninja starts."""
    messages = [
        "Welcome to InfraNinja - Your Infrastructure at Your Command 🥷",
        "InfraNinja: Silently Managing Your Infrastructure 🌐",
        "Ninja Skills Activated - Ready to Deploy! 🚀",
        "The Art of Infrastructure - InfraNinja at Your Service 🛠️"
    ]
    
    border = "=" * 60
    print(f"\n{border}")
    print(f"{random.choice(messages)}")
    print(f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{border}\n")