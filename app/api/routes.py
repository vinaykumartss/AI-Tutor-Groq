from fastapi import APIRouter
from app.core.services import check_grammar, ai_tutor, translate_text, idiom_text
from app.models.text_input import TextInput
from app.utils.responses import success_response
from app.core.prompts import appreciate_text

import random

router = APIRouter()

@router.post('/check-grammar', tags=["Grammar"])
async def api_check_grammar(input_data: TextInput):
    correct_text = check_grammar(input_data.text)
    appreciateText = None
    if input_data.text.lower().strip('?.') == correct_text.lower().strip('?.'):
        appreciateText = random.choice(appreciate_text)

    return {"success": True, "appreciate_text": appreciateText, "text": input_data.text, "correct_text": correct_text}


@router.post('/translation', tags=["Translator"])
async def translation_text(input_data: TextInput):
    translated_text = translate_text(input_data.text)
    return {"success": True,"text": input_data.text, "data": translated_text}

@router.post('/idiom', tags=["Idiom"])
async def idiom_fun(input_data: TextInput):
    idiom_response_text = idiom_text(input_data.text)
    return {"success": True,"text": input_data.text, "data": idiom_response_text}


@router.post('/ai-tutor', tags=['AI-Tutor'])
async def api_ai_tutor(input_data: TextInput):
    correct_text = check_grammar(input_data.text)

    appreciateText = None
    if input_data.text.lower().strip('?.') == correct_text.lower().strip('?.'):
        appreciateText = random.choice(appreciate_text)
    
    return {"success": True, "appreciate_text": appreciateText, "text": input_data.text, "correct_text": correct_text, "data": ai_tutor(prompt=input_data.text)}
    # return success_response(ai_tutor(prompt=correct_text))