from fastapi import APIRouter
from app.core.services import check_grammar, ai_tutor, translate_text, idiom_text, reset_history, ai_interviewer,check_pronunciation
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


@router.post('/ai-tutor/{user_id}', tags=['AI-Tutor'])
async def api_ai_tutor(input_data: TextInput, user_id):
    correct_text = check_grammar(input_data.text)

    appreciateText = None
    if input_data.text.lower().strip('?.') == correct_text.lower().strip('?.'):
        appreciateText = random.choice(appreciate_text)
    
    return {
        "success": True, 
        "appreciate_text": appreciateText, 
        "text": input_data.text, 
        "correct_text": correct_text, 
        "data": ai_tutor(prompt=input_data.text, user_id= user_id)
    }
    # return success_response(ai_tutor(prompt=correct_text))

@router.post('/ai-interviewer/{user_id}', tags=['AI-Tutor'])
async def api_ai_tutor(input_data: TextInput, user_id):
    
    return {
        "success": True, 
        "text": input_data.text, 
        "data": ai_interviewer(prompt=input_data.text, user_id= user_id)
    }
    # return success_response(ai_tutor(prompt=correct_text))


@router.post('/reset-history/{user_id}/{convo_type}', tags=['AI-Tutor'])
async def reset_conversation_history(user_id: str, convo_type: str):
    reset_history(user_id=user_id, convo_type=convo_type)
    return {
        "success": True,
        "message": f"Conversation history for '{convo_type}' has been reset successfully."
    }


@router.post('/check-pronunciation', tags=["Pronunciation"])
async def api_check_pronunciation(input_data: TextInput):
    pronunciation_text = check_pronunciation(input_data.text)
    appreciateText = None
    if input_data.text.lower().strip('?.') == pronunciation_text.lower().strip('?.'):
        appreciateText = random.choice(appreciate_text)

    return {
        "success": True,
        "appreciate_text": appreciateText,
        "text": input_data.text,
        "pronunciation_text": pronunciation_text
    }