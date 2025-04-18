from pydantic import BaseModel

class TextInput(BaseModel):
    text: str


class TranslateRequest(BaseModel):
    text: str
    target_language: str
    
class TranslateResponse(BaseModel):
    translated_text:str