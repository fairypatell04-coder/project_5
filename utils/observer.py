class Event:
    """
    Event system to notify listeners on cache misses or other events
    """
    def __init__(self):
        self.listeners = []

    def register(self, listener):
        self.listeners.append(listener)

    def notify(self, data):
        for listener in self.listeners:
            listener.update(data)


class Listener:
    """
    Base listener class
    """
    def update(self, data):
        print(f"[Observer] Event received: {data}")
