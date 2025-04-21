from pydantic import BaseModel

class TextInput(BaseModel):
    text: str
    new_chat: bool = False