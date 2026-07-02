import requests
import threading
from .Types import Message
from .handlers import process_message
from time import sleep
import json

class Bot:
    """
    this class get token , parse mode (optional) and base_url (optional)"""
    #init
    def __init__(self, token, parse_mode=None, base_url=None):
        self.token = token
        self.base = base_url or f"https://api.telegram.org/bot{token}/"
        self.handlers = []
        self.parse_mode = parse_mode
        self.session = requests.session()

        updates = self.get_updates()
        if updates:
            self.offset = updates[-1]["update_id"] + 1
        else:
            self.offset = 0

    def request(self, method, data=None, files=None):
        """
        this method for managed requests (none for use in your code)
        """
        try:
            r = self.session.post(
                self.base + method,
                data=data,
                files=files,
                timeout=30
            )

            try:
                return r.json()
            except Exception:
                return {
                    "ok": False,
                    "error_code": r.status_code,
                    "description": r.text
                }

        except Exception as e:
            return {
                "ok": False,
                "error": str(e)
            }


    def message_handler(self, commands=None, func=None, content_types = None):
        """
        message handler \n
        use: \n
        @bot.message_handler(["start"]) or @bot.message_handler(func= lambda m: True)
        """
        def decorator(handler):
            
            self.handlers.append({
                "commands": commands or [],
                "filter_func": func,
                "content_types": content_types or [],
                "func": handler
            })
            return handler
        return decorator

    # send message
    def send_message(self, chat_id, text, parse_mode=None):
        """
        send a message to chat id
        """
        data = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode if parse_mode else self.parse_mode
            }
        res = self.request(
            "sendMessage",
            data=data 
        )

        if res.get("ok"):
            return Message(res["result"], bot=self)
        return None
    
    #delete message
    def delete_message(self, chat_id, message_id):
        """
        delete message
        """
        data = {"chat_id": chat_id,
                "message_id": message_id}
        
        self.request("deleteMessage",
                     data=data)
        
    # edit messages
    def edit_message(self, chat_id, message_id, text):
        '''
        edit message with message id
        '''
        data = {"chat_id": chat_id,
                "message_id": message_id,
                "text": text}
        
        self.request("editMessageText", data=data)

    # edit caption
    def edit_caption(self, chat_id, message_id, caption):
        """
        edit caption \n
        for video or photo messsages
        """
        data = {"chat_id": chat_id,
                "message_id": message_id,
                "caption": caption}
        
        self.request("editMessageCaption", data=data)

    
    def send_message_reaction(self, chat_id, message_id, emoji, is_big=False):
        """ send message reaction \n
         avaible reaction on https://core.telegram.org/bots/api#reactiontypeemoji """
        data = {
            "chat_id": chat_id,
            "message_id": message_id,
            "reaction": json.dumps([
                {
                    "type": "emoji",
                    "emoji": emoji
                }
            ], ensure_ascii=False),
            "is_big": is_big
        }
        return self.request("setMessageReaction", data=data)
    
    
    def send_photo(self, chat_id, photo, caption=None, reply_to_message_id=None, parse_mode=None):
        """
        send photo with URL or photo file
        """
        data = {
            "chat_id": chat_id,
            "caption": caption,
            "reply_to_message_id": reply_to_message_id,
            "parse_mode": parse_mode or self.parse_mode
        }

        if isinstance(photo, str):
            data["photo"] = photo
            res = self.request("sendPhoto", data=data)
        else:
            files = {"photo": photo}
            res = self.request("sendPhoto", data=data, files=files)

        if res.get("ok"):
            return Message(res["result"], bot=self)
        return None

    
    def reply_to(self, message, text, message_id=None, parse_mode=None):
        """
        reply to message \n
        reply to selected message with message_id
        """
        data = {"chat_id": message.chat.id,
                "text": text,
                'reply_to_message_id': message_id or message.message_id,
                "parse_mode": parse_mode if parse_mode else self.parse_mode
                }
        
        res = self.request("sendMessage", data=data)
        if res.get("ok"):
            return Message(res["result"], bot=self)
        return None
    
    #send chat action
    def send_chat_action(self, chat_id, action):
        """
        send chat action \n
        type of actions =  \n
        typing for text messages, \n 
        upload_photo for photos, \n 
        record_video or upload_video for videos, \n
        record_voice or upload_voice for voice notes, \n
        upload_document for general files, \n
        choose_sticker for stickers, \n
        find_location for location data, \n
        record_video_note or upload_video_note for video notes.
        """
        return self.request("sendChatAction", data={"chat_id": chat_id, "action": action})

    # pin a message
    def pin_message(self, chat_id, message_id):
        """
        pin message with message id
        """
        data = {"chat_id": chat_id,
                "message_id": message_id}
        
        return self.request("pinChatMessage",
                            data=data)
    
    #unpin messages
    def unpin_message(self, chat_id, message_id=None):
        """
        unpin messages \n
        if message id is None , unpinned all messages
        """
        if message_id != None:
            #unpin selected message
            return self.request("unpinChatMessage", data={"chat_id":chat_id, "message_id":message_id})
        else:
            #unpin all messages
            return self.request("unpinAllChatMessages", data={"chat_id": chat_id})

    
    def get_updates(self, offset=None, timeout=30):
        """
        get updates (not for use in your code)
        """
        data = {"timeout": timeout}

        if offset is not None:
            data["offset"] = offset

        res = self.request("getUpdates", data=data)
        if not res.get("ok"):
            print("Telegram API error:", res)
            return []

        return res.get("result", [])

    # download file
    def download_file(self, file_id, file_name = "image.png"):
        """
        download file with file id
        if file name is empty , file named image.png
        """
        
        file = self.request("getFile", data={"file_id":file_id})
        if not file.get("ok"):
            return None
        path = file["result"]["file_path"]
        
        url = f"https://api.telegram.org/file/bot{self.token}/{path}"
        response = self.session.get(url, timeout=30)
        if response.status_code == 200:
            with open(file_name, "wb") as f:
                f.write(response.content)
        
        return {
            "ok": True,
            "file_path": file_name,
            "telegram_path": path
        }
           
    #polling
    def _polling(self, timeout):
        """
        polling (none for use in your code)
        """
        while True:
            try:
                updates = self.get_updates(
                    offset=self.offset,
                    timeout=timeout
                )

                for update in updates:
                    try:
                        self.offset = update["update_id"] + 1

                        if "message" not in update:
                            continue

                        process_message(self, update["message"])

                    except Exception as e:
                        print("Update Processing Error:", e)

            except Exception as e:
                print("Polling Error:", e)
                sleep(2)

    def polling(self, timeout=30):
        """
        polling your bot
        """
        threading.Thread(
            target=self._polling,
            args=(timeout,),
        ).start()

