from .Types import Message


#processing messages
def process_message(self, data):
    text = data.get("text")


    msg = Message(data)

    for handler in self.handlers:

        if handler["commands"]:
            commands = handler["commands"]
            for cmd in commands:
                if text and text.startswith(f"/{cmd}") :
                    try:
                        handler["func"](msg)
                    except Exception as e:
                        print(e)
                    break

        # content type handlers
        if handler["content_types"]:
            if msg.content_type in handler["content_types"]:
                handler["func"](msg)
                continue
        
        if handler["filter_func"]:
            if handler['filter_func'](msg):
                try:
                    handler["func"](msg)
                except Exception as e:
                    print(e)
                break
