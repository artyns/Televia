from .Types import Message, CallbackQuery


def process_message(self, data):
    text = data.get("text")
    msg = Message(data)

    for handler in self.handlers:
        if handler.get("type") != "message":
            continue

        if handler["commands"]:
            for cmd in handler["commands"]:
                if text and text.startswith(f"/{cmd}"):
                    try:
                        handler["func"](msg)
                    except Exception as e:
                        print(e)
                    return

        if handler["content_types"]:
            if msg.content_type in handler["content_types"]:
                try:
                    handler["func"](msg)
                except Exception as e:
                    print(e)
                return

        if handler["filter_func"]:
            if handler["filter_func"](msg):
                try:
                    handler["func"](msg)
                except Exception as e:
                    print(e)
                return


def process_callback_query(self, data):
    call = CallbackQuery(data)

    for handler in self.handlers:
        if handler.get("type") != "callback_query":
            continue

        filt = handler.get("filter_func")
        try:
            if filt is None or filt(call):
                handler["func"](call)
                return
        except Exception as e:
            print(e)


def process_guest_message(self, data):
    text = data.get("text")
    msg = Message(data)

    for handler in self.handlers:
        if handler.get("type") != "guest_message":
            continue

        if handler["filter_func"]:
            if handler["filter_func"](msg):
                try:
                    handler["func"](msg)
                except Exception as e:
                    print(e)
                return