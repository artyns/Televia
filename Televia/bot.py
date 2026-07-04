import requests
import threading
from .Types import Message, SentGuestMessage
from .handlers import process_message, process_callback_query, process_guest_message
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

    def request(self, method, data=None, json_data=None, files=None):
        """
        this method for managed requests (none for use in your code)
        """
        try:
            r = self.session.post(
                self.base + method,
                data=data,
                files=files,
                json=json_data,
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


    def message_handler(self, commands=None, func=None, content_types=None):
        """
        message handler
        use:
        @bot.message_handler(commands=["start"])
        @bot.message_handler(func=lambda m: True)
        """
        def decorator(handler):
            self.handlers.append({
                "type": "message",
                "commands": commands or [],
                "filter_func": func,
                "content_types": content_types or [],
                "func": handler
            })
            return handler
        return decorator

    def callback_query_handler(self, func=None):
        def decorator(handler):
            self.handlers.append({
                "type": "callback_query",
                "commands": [],
                "content_types": [],
                "filter_func": func,
                "func": handler
            })
            return handler
        return decorator
    
    def answer_callback_query(self, callback_query_id, text=None, show_alert=None):
        data = {
            "callback_query_id": callback_query_id
        }

        if text is not None:
            data["text"] = text

        if show_alert is not None:
            data["show_alert"] = show_alert

        return self.request("answerCallbackQuery", data=data)

    def guest_message_handler(self, func=None, content_types=None):
        """
        message handler
        use:
        @bot.message_handler(commands=["start"])
        @bot.message_handler(func=lambda m: True)
        """
        def decorator(handler):
            self.handlers.append({
                "type": "guest_message",
                "commands": [],
                "filter_func": func,
                "content_types": content_types or [],
                "func": handler
            })
            return handler
        return decorator


    # send message
    def send_message(self, chat_id, text, parse_mode=None,reply_markup=None, protect_content=False, message_effect_id=None):
        """
        send a message to chat id
        """
        data = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode if parse_mode else self.parse_mode,
            "protect_content": protect_content,
            "message_effect_id": message_effect_id
            }
        
        if reply_markup is not None:
            if hasattr(reply_markup, "to_dict"):
                data["reply_markup"] = json.dumps(reply_markup.to_dict())

        res = self.request(
            "sendMessage",
            data=data 
        )

        if res.get("ok"):
            return Message(res["result"], bot=self)
        return None
    
    def send_check_list(self, chat_id, checklist):
        data = {
            "chat_id": chat_id,
            "checklist": json.dumps(checklist.to_dict())
        }

        res = self.request("sendChecklist", data=data)
        if res["ok"] == True:
            return Message(res["result"])
        else:
            return res

    def answer_guest_query(self, guest_query_id, result):

        data = {
            "guest_query_id": guest_query_id,
        }
        
        if hasattr(result, "to_dict"):
            data["result"] = result.to_dict()
        elif isinstance(result, dict):
            data["result"] = result
        else:
            raise TypeError(f"Invalid result type: {type(result)}")

        res = self.request("answerGuestQuery", json_data=data)

        if res["ok"] == True:
            return SentGuestMessage(res["result"])
        else:
            return res

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
    def edit_message(self, chat_id, message_id, text, parse_mode=None, reply_markup=None):
        '''
        edit message with message id
        '''
        data = {"chat_id": chat_id,
                "message_id": message_id,
                "text": text,
                "parse_mode": parse_mode or self.parse_mode,
                
                }
        
        if reply_markup is not None:
            if hasattr(reply_markup, "to_dict"):
                data["reply_markup"] = json.dumps(reply_markup.to_dict())
        
        self.request("editMessageText", data=data)

    # edit caption
    def edit_caption(self, chat_id, message_id, caption, parse_mode=None, reply_markup=None):
        """
        edit caption \n
        for video or photo messsages
        """
        data = {"chat_id": chat_id,
                "message_id": message_id,
                "caption": caption,
                "parse_mode": parse_mode or self.parse_mode,
            
                }
        
        if reply_markup is not None:
            if hasattr(reply_markup, "to_dict"):
                data["reply_markup"] = json.dumps(reply_markup.to_dict())
        
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
    
    
    def send_photo(self, chat_id, photo, caption=None, reply_to_message_id=None, parse_mode=None, has_spoiler=False, protect_content=False, message_effect_id=None, reply_markup=None):
        """
        send photo with URL or photo file
        """
        data = {
            "chat_id": chat_id,
            "caption": caption,
            "reply_to_message_id": reply_to_message_id,
            "parse_mode": parse_mode or self.parse_mode,
            "has_spoiler": has_spoiler,
            "protect_content": protect_content,
            "message_effect_id": message_effect_id,
        }

        if reply_markup is not None:
            if hasattr(reply_markup, "to_dict"):
                data["reply_markup"] = json.dumps(reply_markup.to_dict())

        if isinstance(photo, str):
            data["photo"] = photo
            res = self.request("sendPhoto", data=data)
        else:
            files = {"photo": photo}
            res = self.request("sendPhoto", data=data, files=files)

        if res.get("ok"):
            return Message(res["result"], bot=self)
        return None

    
    def reply_to(self, message, text, message_id=None, parse_mode=None,protect_content=False, message_effect_id=None, reply_markup=None):
        """
        reply to message \n
        reply to selected message with message_id
        """
        data = {"chat_id": message.chat.id,
                "text": text,
                'reply_to_message_id': message_id or message.message_id,
                "parse_mode": parse_mode if parse_mode else self.parse_mode,
                "protect_content": protect_content,
                "message_effect_id": message_effect_id,
                
                }
        
        if reply_markup is not None:
            if hasattr(reply_markup, "to_dict"):
                data["reply_markup"] = json.dumps(reply_markup.to_dict())
        
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


    def leave_chat(self, chat_id):
        data = {"chat_id": chat_id}
        return self.request("leaveChat", data=data)

    def ban_chat_memeber(self, chat_id, user_id):
        data = {
            "chat_id": chat_id,
            "user_id": user_id
        }

        return self.request("banChatMember", data=data)
    
    def unban_chat_member(self, chat_id, user_id, only_if_banned=True):
        data = {
            "chat_id": chat_id,
            "user_id": user_id,
            "only_if_banned": only_if_banned
        }

        return self.request("unbanChatMember", data=data)

    def send_poll(self,
                chat_id,
                question,
                options, 
                description =None,
                poll_type=None,
                question_parse_mode=None,
                is_anonymous=None, 
                allows_multiple_answers=None, 
                allows_revoting=None, 
                allow_adding_options=None,
                shuffle_options=None,
                correct_option_ids=None,
                reply_markup=None):
        
        """
        send poll \n
        poll types: quiz or regular (defaults to regular) \n
        correct_option_ids only for quiz type \n
        correct_option_ids A JSON-serialized list of monotonically increasing 0-based identifiers of the correct answer options, required for polls in quiz mode \n

        """
        data = {
            "chat_id": chat_id,
            "question": question,
            "options": json.dumps(options, ensure_ascii=False),
            "description": description,
            "question_parse_mode": question_parse_mode or self.parse_mode,
            "is_anonymous": is_anonymous,
            "allows_multiple_answers": allows_multiple_answers,
            "allows_revoting": allows_revoting,
            "allow_adding_options": allow_adding_options,
            "reply_markup": reply_markup,
            "type": poll_type,
            "correct_option_ids": json.dumps(correct_option_ids)


        }

        return self.request("sendPoll", data=data)

    def restrict_chat_member(self, chat_id, user_id, permissions):
        if hasattr(permissions, "to_dict"):
            permissions = permissions.to_dict()

        data = {"chat_id": chat_id,
                "user_id": user_id,
                "permissions": json.dumps(permissions)}
        
        return self.request("restrictChatMember", data=data)

    def set_memeber_tag(self, chat_id, user_id, tag):
        data = {
            "chat_id": chat_id,
            "user_id": user_id,
            "tag": tag
        }

        return self.request("setChatMemberTag", data=data)
    
    def create_topic(self, chat_id, name, icon_color=None):
        """Color of the topic icon in RGB format. Currently, must be one of 7322096 (0x6FB9F0), 16766590 (0xFFD67E), 13338331 (0xCB86DB), 9367192 (0x8EEE98), 16749490 (0xFF93B2), or 16478047 (0xFB6F5F)."""

        data = {"chat_id": chat_id,
                "name": name,
                "icon_color": icon_color}
        return self.request("createForumTopic", data=data)

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
        polling (not for use in your code)
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

                        if "message" in update:
                            process_message(self, update["message"])

                        elif "callback_query" in update:
                            process_callback_query(self, update["callback_query"])

                        elif "guest_message" in update:
                            process_guest_message(self, update["guest_message"])

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

