from websocket import create_connection
from websocket._exceptions import WebSocketBadStatusException
from aiogram.types import Message


def instrument_supported(instrument: Message | str | None) -> bool:
    if type(instrument) is Message:
        instrument = instrument.text
    url = f"ws://127.0.0.1:8000/ws/orderbox/{instrument}/"
    try:
        ws = create_connection(url)
        ws.close()
    except WebSocketBadStatusException:
        return False
    return True
