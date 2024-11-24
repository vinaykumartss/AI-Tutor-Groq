from fastapi import APIRouter
from app.core.services import check_grammar, ai_tutor
from app.models.text_input import TextInput
from app.utils.responses import success_response
from app.core.prompts import appreciate_text

import random

router = APIRouter()


@router.get("/")
async def read_root():
    return {"message": "Hello, Azure!"}

@router.post('/check-grammar', tags=["Grammar"])
async def api_check_grammar(input_data: TextInput):

    correct_text = check_grammar(input_data.text)
    if input_data.text.lower().strip('?.') == correct_text.lower().strip('?.'):
        return success_response(random.choice(appreciate_text))
    return success_response(correct_text)

@router.post('/ai-tutor', tags=['AI-Tutor'])
async def api_ai_tutor(input_data: TextInput):
    correct_text = check_grammar(input_data.text)
    return success_response(ai_tutor(prompt=correct_text))