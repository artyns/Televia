import json

class Message:
    def __init__(self, data, bot=None):
        self.raw = data
        self.bot = bot

        self.message_id = data.get("message_id")
        self.text = data.get("text")
        self.caption = data.get("caption")
        self.receiver_user = data.get("receiver_user")
        self.ephemeral_message_id = data.get("ephemeral_message_id") if data.get("ephemeral_message_id") else None
        self.date = data.get("date")

        photo_data = data.get("photo")
        self.photo = photo(photo_data[-1]) if photo_data else None
        
        self.chat = Chat(data.get("chat", {}))
        self.from_user = User(data.get("from", {}))
        self.forward_from = User(data["forward_from"]) if data.get("forward_from") else None
        self.reply_to_message = Message(data["reply_to_message"], bot=bot) if data.get("reply_to_message") else None
        self.quote = Quote(data.get("TextQuote")) if data.get("TextQuote") else None

        self.guest_query_id = data["guest_query_id"] if data.get("guest_query_id") else None

#chat data    
class Chat:
    def __init__(self, data):
        self.data = data
        self.id = data.get("id")
        self.type = data.get("type")


#user data
class User:
    def __init__(self, data):
        self.id = data.get("id")
        self.lang_code = data.get("language_code")
        self.username = data.get("username")
        self.first_name = data.get("first_name")
        self.last_name = data.get("last_name")



#photo data
class photo:
    def __init__(self, data):
        self.file_id = data.get("file_id")


class Quote:
    def __init__(self, data):
        self.text = data.get("text")
        self.position = data.get("position")
        self.is_manual = data.get("is_manual")


#inline keyboard button
class InlineKeyboardButton:
    """
    Inline keyboard button \n
    callbackdata : optional \n
    url: optional \n
    style: optional \n
    types of style: danger(red), success(green), primary(blue)
    """
    def __init__(self, text, callback_data=None, url=None, style=None, CopyTextButton=None):
        self.text = text
        self.callback_data = callback_data
        self.url = url
        self.style = style
        self.CopyTextButton = CopyTextButton

    def to_dict(self):
        data = {"text": self.text}

        if self.callback_data is not None:
            data["callback_data"]= self.callback_data
        
        if self.url is not None:
            data["url"] = self.url

        if self.style is not None:
            data["style"] = self.style

        if self.CopyTextButton is not None:
            data["copy_text"] = {"text": self.CopyTextButton}

        return data
    
#inline keyboard markup
class InlineKeyboardMarkup:
    def __init__(self):
        self.inline_keyboard = []

    def add(self, *Buttons):
        row = []
        for button in Buttons:
            if isinstance(button, InlineKeyboardButton):
                row.append(button.to_dict())
            else:
                raise TypeError("only InlineKeyboardButton is allowed")
            
        self.inline_keyboard.append(row)

    def to_dict(self):
        return {"inline_keyboard": self.inline_keyboard}
    
    def to_json(self):
        return json.dumps(self.to_dict())


class CallbackQuery:
    def __init__(self, data):
        self.id = data.get("id")
        self.data = data.get("data")
        self.chat_instance = data.get("chat_instance")
        self.inline_message_id = data.get("inline_message_id")
        self.from_user = data.get("from")

        self.message = Message(data["message"]) if data.get("message") else None

class permissions:
    def __init__(self, can_send_messages=None,
                 can_send_audios=None,
                 can_send_documents=None,
                 can_send_photos=None,
                 can_send_videos=None,
                 can_send_video_notes=None,
                 can_send_voice_notes=None,
                 can_send_polls=None,
                 can_send_other_messages=None,
                 can_add_web_page_previews=None,
                 can_react_to_messages=None,
                 can_edit_tag=None,
                 can_change_info=None,
                 can_invite_users=None,
                 can_pin_messages=None,
                 can_manage_topics=None):
        
        self.can_send_messages=can_send_messages
        self.can_send_audios=can_send_audios
        self.can_send_documents=can_send_documents
        self.can_send_photos=can_send_photos
        self.can_send_videos=can_send_videos
        self.can_send_video_notes=can_send_video_notes
        self.can_send_voice_notes=can_send_voice_notes
        self.can_send_polls=can_send_polls
        self.can_send_other_messages=can_send_other_messages
        self.can_add_web_page_previews=can_add_web_page_previews
        self.can_react_to_messages=can_react_to_messages
        self.can_edit_tag=can_edit_tag
        self.can_change_info=can_change_info
        self.can_invite_users=can_invite_users
        self.can_pin_messages=can_pin_messages
        self.can_manage_topics=can_manage_topics

    def to_dict(self):
        data = {}

        for key, value in self.__dict__.items():
            if value is not None:
                data[key] = value
        return data

class InlineQueryResultArticle:
    def __init__(self, id, title, input_message_content,description=None, reply_markup=None):
        self.type = "article"
        self.id = id
        self.title = title
        self.input_message_content = input_message_content
        self.reply_markup = reply_markup
        self.description = description or ""

    def to_dict(self):
        data = {
            "id": self.id,
            "title": self.title,
            "input_message_content": self.input_message_content.to_dict(),
            "description": self.description,
            "type": self.type
        }

        if self.reply_markup is not None:
            if hasattr(self.reply_markup, "to_dict"):
                data["reply_markup"] = self.reply_markup.to_dict()

        return data
       
class InputTextMessageContent:
    def __init__(self, message_text, parse_mode=None):
        self.message_text = message_text
        self.parse_mode = parse_mode or ""

    def to_dict(self):
        return {
            "message_text": self.message_text,
            "parse_mode": self.parse_mode
        }
        
class SentGuestMessage:
    def __init__(self, data):
        self.inline_message_id = data["inline_message_id"] if data.get("inline_message_id") else None

class InputChecklist:
    def __init__(self, title):
        self.title = title
        self.tasks = []

    def add(self, *tasks):
        for task in tasks:
            if isinstance(task, InputChecklistTask):
                self.tasks.append(task.to_dict())
            else:
                raise TypeError("only InputChecklistTask is allowed")

    def to_dict(self):
        return {
            "title": self.title,
            "tasks": self.tasks
        }

class InputChecklistTask:
    def __init__(self, id, text):
        self.id = id
        self.text = text

    def to_dict(self):
        return {
            "id": self.id,
            "text": self.text
        }
    
class UserProfilePhotos:
    def __init__(self, data):
        self.total_count = data.get("total_count")
        photo = data.get("photos")
        self.photos = PhotoSize(photo[0][-1])

class PhotoSize:
    def __init__(self, data):
        self.file_id = data.get("file_id")
        self.file_unique_id = data.get("file_unique_id")
        self.width = data.get("width")
        self.height = data.get("height")
        self.file_size = data.get("file_size")

class ChatFullInfo:
    def __init__(self, data):
        self.ALLdata = str(data)
        self.id = data.get("id")
        self.type = data.get("type")
        self.title = data.get("title")
        self.username = data.get("username")
        self.first_name = data.get("first_name")
        self.last_name = data.get("last_name")
        self.is_forum = data.get("is_forum")
        self.is_direct_messages = data.get("is_direct_messages")
        self.accent_color_id = data.get("accent_color_id")
        self.max_reaction_count = data.get("max_reaction_count")
        self.bio = data.get("bio")
        self.join_to_send_messages = data.get("join_to_send_messages")
        self.join_by_request = data.get("join_by_request")
        self.description = data.get("description")

class ForceReply:
    def __init__(self, force_reply=None, input_field_placeholder=None, selective=None):
        self.force_reply = force_reply or True
        self.input_field_placeholder = input_field_placeholder
        self.selective = selective

    def to_dict(self):
        data = {
            "force_reply": self.force_reply,
        }

        if self.force_reply is not None:
            data["force_reply"] = self.force_reply
        if self.input_field_placeholder is not None:
            data ["input_field_placeholder"] = self.input_field_placeholder

        return data
    
class InputRichMessage:
    def __init__(self, html="", markdown="", blocks=[], media=[], is_rtl=False, skip_entity_detection=False):
        self.html = html
        self.markdown = markdown
        self.blocks = blocks
        self.media = media
        self.is_rtl = is_rtl
        self.skip_entity_detection = skip_entity_detection
    
    def to_dict(self):
        return {
            "html": self.html,
            "markdown": self.markdown,
            "block": self.blocks,
            "media": self.media,
            "is_rtl": self.is_rtl,
            "skip_entity_detection": self.skip_entity_detection
        }

class inlineQuery:
    def __init__(self, data):
        self.id = data.get("id")
        self.from_user = User(data.get("from"))
        self.chat_type = data.get("chat_type")
        self.query = data.get("query")
        self.offset = data.get("offset")
        
       


