class Message:
    def __init__(self, data, bot=None):
        self.raw = data
        self.bot = bot

        self.message_id = data.get("message_id")
        self.text = data.get("text")
        self.caption = data.get("caption")

        photo_data = data.get("photo")
        self.photo = photo(photo_data[-1]) if photo_data else None
        
        self.chat = Chat(data.get("chat", {}))
        self.from_user = User(data.get("from", {}))
        self.forward_from = User(data["forward_from"]) if data.get("forward_from") else None
        self.reply_to_message = Message(data["reply_to_message"], bot=bot) if data.get("reply_to_message") else None

#chat data    
class Chat:
    def __init__(self, data):
        self.data = data
        self.id = data.get("id")


#user data
class User:
    def __init__(self, data):
        self.id = data.get("id")
        self.lang_code = data.get("language_code")
        self.user_name = data.get("username")
        self.first_name = data.get("first_name")
        self.last_name = data.get("last_name")



#photo data
class photo:
    def __init__(self, data):
        self.file_id = data.get("file_id")



