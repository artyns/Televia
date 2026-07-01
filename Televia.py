import requests
import threading

class Bot:
    #init
    def __init__(self, token, parse_mode=None, base_url=None):
        self.token = token
        self.base = f"https://api.telegram.org/bot{token}/" or base_url
        self.handlers = []
        self.parse_mode = parse_mode
        self.session = requests.session()

        updates = self.get_updates()["result"]
        if updates:
            self.offset = updates[-1]["update_id"] + 1
        else:
            self.offset = 0

    # requests manager (not for use in your code)
    def request(self, method, **data):
        try:
            r = self.session.post(self.base + method, data=data, timeout=30)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            print(e)
            return {"ok": False}

    # send message
    def send_message(self, chat_id, text, parse_mode=None):
        return self.request(
            "sendMessage",
            chat_id=chat_id,
            text=text,
            parse_mode = parse_mode if parse_mode else self.parse_mode
        )
    
    # send a Photo
    def send_photo(self, chat_id, photo, caption=None, reply_to_message_id=None, parse_mode=None):
        return self.request(
            "sendPhoto",
            chat_id=chat_id,
            photo=photo,
            caption=caption,
            reply_to_message_id=reply_to_message_id,
            parse_mode = parse_mode if parse_mode else self.parse_mode
        )
    
    # reply message
    def reply_to(self, message, text, parse_mode=None):
        
        
        return self.request(
            "sendMessage",
            chat_id=message.chat.id,
            text=text,
            reply_to_message_id = message.message_id,
            parse_mode = parse_mode if parse_mode else self.parse_mode
        )
    
    # pin a message
    def pin_message(self, chat_id, message_id):
        return self.request("pinChatMessage",
                            chat_id= chat_id,
                            message_id= message_id)
    
    #unpin messages
    def unpin_message(self, chat_id, message_id=None):
        if message_id != None:
            #unpin selected message
            return self.request("unpinChatMessage", chat_id=chat_id, message_id=message_id)
        else:
            #unpin all messages
            return self.request("unpinAllChatMessages", chat_id=chat_id)

    # get updates (not for use in your code)
    def get_updates(self, offset=None, timeout=30):
        data = {"timeout": timeout}

        if offset is not None:
            data["offset"] = offset

        return self.request("getUpdates", **data)

    # download file
    def get_file(self, file_id, file_name = "image.png"):
        
        file = self.request("getFile", file_id= file_id)
        if not file.get("ok"):
            return None
        path = file["result"]["file_path"]
        
        url = f"https://api.telegram.org/file/bot{self.token}/{path}"
        response = self.session.get(url, timeout=30)
        if response.status_code == 200:
            with open(file_name, "wb") as f:
                f.write(response.content)
        
        return response.status_code

    # message handler
    # use 
    # @bot.message_handler(["start"]) or @bot.message_handler(func= lambda m: True)
    def message_handler(self, commands=None, func=None):
        def decorator(handler):
            self.handlers.append({
                "commands": commands,
                "filter_func": func,
                "func": handler
            })
            return handler
        return decorator
    
    #processing messages
    def process_message(self, data):
        text = data.get("text")


        msg = Message(data)

        for handler in self.handlers:

            if handler["commands"]:
                commands = handler["commands"]
                for cmd in commands:
                    if text and text == f"/{cmd}":
                        try:
                            handler["func"](msg)
                        except Exception as e:
                            print(e)
                        break
            elif handler["filter_func"]:
                if handler['filter_func'](msg):
                    try:
                        handler["func"](msg)
                    except Exception as e:
                        print(e)
                    break
            
    #polling
    def _polling(self, timeout):
        while True:
            try:
                updates = self.get_updates(
                    offset=self.offset,
                    timeout=timeout
                )["result"]

                for update in updates:
                    self.offset = update["update_id"] + 1

                    if "message" not in update:
                        continue

                    self.process_message(update["message"])

            except Exception as e:
                print("Polling Error:", e)

    def polling(self, timeout=30):
        threading.Thread(
            target=self._polling,
            args=(timeout,),
        ).start()


#message data
class Message:
    def __init__(self, data):
        self.raw_ = data
        self.text = data.get("text")
        photo_data = data.get("photo")
        self.photo = photo(photo_data[-1]) if photo_data else None
        self.message_id = data.get("message_id")
        self.chat = Chat(data.get("chat", {}))
        self.from_user = User(data.get("from", {}))
        forward = data.get("forward_from")
        self.forward_from = forward_from(data["forward_from"]) if forward else None
        self.reply_to_message = reply_to_message(data["reply_to_message"]) if data.get("reply_to_message") else None


#chat data    
class Chat:
    def __init__(self, data):
        self.data = data
        self.id = data.get("id")


#user data
class User:
    def __init__(self, data):
        self.user_id = data.get("id")
        self.lang_code = data.get("language_code")
        self.user_name = data.get("username")
        self.first_name = data.get("first_name")
        self.last_name = data.get("last_name")


#forward from data
class forward_from:
    def __init__(self, data):
        self.id = data.get("id")
        self.first_name = data.get("first_name")
        self.last_name = data.get("last_name")
        self.user_name = data.get("username")


#photo data
class photo:
    def __init__(self, data):
        self.photo_id = data.get("file_id")


#replyed message data
class reply_to_message:
    def __init__(self, data):
        self.message_id = data["message_id"]
        self.user = User(data.get("from", {}))
        self.text = data.get("text")

