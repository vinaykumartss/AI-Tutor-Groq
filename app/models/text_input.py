from pydantic import BaseModel

class TextInput(BaseModel):
    text: str
    new_chat: bool = False

class TranslateRequest(BaseModel):
    text: str
    target_language: str
    
class TranslateResponse(BaseModel):
    translated_text:str
