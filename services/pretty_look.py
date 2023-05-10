import json


def quote_pretty(quote: str | bytes, instrument: str) -> str:
    quote_json = json.loads(quote)
    ask = quote_json["ask"]
    bid = quote_json["bid"]
    return f"{instrument}\n\nask: {ask}\n\nbid: {bid}"


def order_pretty(order: dict) -> str:
    view_pretty = ""
    for key in order:
        view_pretty += f"{key}: {order[key]} \n"
    return view_pretty
