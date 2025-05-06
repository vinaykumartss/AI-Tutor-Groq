from fastapi import APIRouter
from app.core.services import *
from app.models.text_input import TextInput, Translate_Many_Request, TranslateRequest

from app.utils.responses import success_response
from app.core.prompts import appreciate_text, bpo_interview_prompt, country_knowledge_prompt, customer_care_prompt, government_job_prompt, hobbies_prompt, hr_interview_prompt, ielts_prompt, role_model_prompt, social_media_prompt, toefl_prompt

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

@router.post('/translate-hindi', tags=["Translator"])
async def translation_text_to_hindi(input_data: TextInput):
    translated_text = translate_text_to_hindi(input_data.text)
    return {
        "success": True,
        "text": input_data.text,
        "data": translated_text
    }
    
@router.post("/translate-english-to-any", tags=["Translator"])
async def translation_text_to_language(input_data: TranslateRequest):
    translated = translate_text_to_language(input_data.text, input_data.target_language)
    return {
        "success": True,
        "text": input_data.text,
        "target_language": input_data.target_language,
        "data": translated
    }

@router.post("/translator-to-any", tags=["Translator"])
async def translate_text_api(input_data: Translate_Many_Request):
    translated = translate_text(input_data.text, input_data.source_language, input_data.target_language)
    return {
        "success": True,
        "source_language": input_data.source_language,
        "target_language": input_data.target_language,
        "original_text": input_data.text,
        "translated_text": translated
    }

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
        "data": ai_tutor(prompt=input_data.text, user_id= user_id,new_chat=input_data.new_chat)
    }
    # return success_response(ai_tutor(prompt=correct_text))

@router.post('/ai-interviewer/{user_id}', tags=['user'])
async def api_ai_tutor(input_data: TextInput, user_id):
    correct_text = check_grammar(input_data.text)

    appreciateText = None
    if input_data.text.lower().strip('?.') == correct_text.lower().strip('?.'):
        appreciateText = random.choice(appreciate_text)
    
    return {
        "success": True, 
        "text": input_data.text, 
        "correct_text": correct_text, 
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
    
@router.post('/daily-routine/{user_id}', tags=["Discuss"])
async def get_daily_routine_task(input_data: TextInput,user_id):
    task = check_grammar(input_data.text)
    
    appreciateText = None
    if input_data.text.lower().strip('?.') == task.lower().strip('?.'):
        appreciateText = random.choice(appreciate_text)
    return {
        "success": True,
        "appreciate_text": appreciateText,
        "text": input_data.text,
        "correct_text": task,
        "data": daily_routine_task(input_data.text, user_id=user_id)  
    }
    
@router.post('/hobbies/{user_id}', tags=["Discuss"])
async def api_hobbies(input_data: TextInput, user_id: str):
    task = check_grammar(input_data.text)
    appreciateText = None

    if input_data.text.lower().strip('?.') == task.lower().strip('?.'):
        appreciateText = random.choice(appreciate_text)

    prompt = hobbies_prompt(input_data.text)

    return {
        "success": True,
        "appreciate_text": appreciateText,
        "text": input_data.text,
        "correct_text": task,
        "data": ai_hobbies_response(prompt, user_id=user_id)
    }

@router.post('/about-country/{user_id}', tags=["Discuss"])
async def api_about_country(input_data: TextInput, user_id: str):
    task = check_grammar(input_data.text)
    appreciateText = None
    if input_data.text.lower().strip('?.') == task.lower().strip('?.'):
        appreciateText = random.choice(appreciate_text)
    corrected_text = input_data.text.strip().capitalize()
    prompt = country_knowledge_prompt(corrected_text)
    country_data = about_country(prompt, user_id=user_id)
    return {
        "success": True,
        "appreciate_text": appreciateText,
        "text": input_data.text,
        "correct_text": corrected_text,
        "data": country_data  
    }

    
@router.post('/role-model/{user_id}', tags=["Discuss"])
async def api_role_model(input_data: TextInput, user_id: str):
    task = check_grammar(input_data.text)
    appreciateText = None
    if input_data.text.lower().strip('?.') == task.lower().strip('?.'):
        appreciateText = random.choice(appreciate_text)
    prompt = role_model_prompt(input_data.text)
    return {
        "success": True,
        "appreciate_text": appreciateText,
        "text": input_data.text,
        "correct_text": task,
        "data": ai_role_model(prompt, user_id=user_id) 
    }

    
@router.post('/social-media/{user_id}', tags=["Discuss"])
async def api_social_media(input_data: TextInput, user_id: str):
    task = check_grammar(input_data.text)
    appreciateText = None
    if input_data.text.lower().strip('?.') == task.lower().strip('?.'):
        appreciateText = random.choice(appreciate_text)
    platform_name = input_data.text.strip()  
    prompt = social_media_prompt(platform_name)
    return {
        "success": True,
        "appreciate_text": appreciateText,
        "text": input_data.text,
        "correct_text": task,
        "data": ai_social_media(prompt, user_id=user_id)  
    }

    
@router.post('/childhood-memory/{user_id}', tags=["Discuss"])
async def api_childhood_memory(input_data: TextInput,user_id):
    task = check_grammar(input_data.text)
    
    appreciateText = None
    if input_data.text.lower().strip('?.') == task.lower().strip('?.'):
        appreciateText = random.choice(appreciate_text)
    return {
        "success": True,
        "appreciate_text": appreciateText,
        "text": input_data.text,
        "correct_text": task,
        "data": ai_childhood_memory(input_data.text, user_id=user_id)  
    }

@router.post('/hr-interview/{user_id}', tags=["Interview"])
async def api_hr_interview(input_data: TextInput, user_id: str):
    task = check_grammar(input_data.text)
    appreciateText = None
    if input_data.text.lower().strip('?.') == task.lower().strip('?.'):
        appreciateText = random.choice(appreciate_text)
    prompt = hr_interview_prompt(input_data.text)
    return {
        "success": True,
        "appreciate_text": appreciateText,
        "text": input_data.text,
        "correct_text": task,
        "data": ai_hr_interview(prompt, user_id=user_id) 
    }

@router.post('/gov-job/{user_id}', tags=["Interview"])
async def api_government_job(input_data: TextInput, user_id: str):
    task = check_grammar(input_data.text)
    appreciateText = None
    if input_data.text.lower().strip('?.') == task.lower().strip('?.'):
        appreciateText = random.choice(appreciate_text)
    prompt = government_job_prompt(input_data.text)
    return {
        "success": True,
        "appreciate_text": appreciateText,
        "text": input_data.text,
        "correct_text": task,
        "data": ai_government_job(prompt, user_id=user_id)
    }
    
@router.post('/customer-care/{user_id}', tags=["Interview"])
async def api_customer_care(input_data: TextInput, user_id: str):
    task = check_grammar(input_data.text)
    appreciateText = None
    if input_data.text.lower().strip('?.') == task.lower().strip('?.'):
        appreciateText = random.choice(appreciate_text)
    prompt = customer_care_prompt(input_data.text)
    return {
        "success": True,
        "appreciate_text": appreciateText,
        "text": input_data.text,
        "correct_text": task,
        "data": ai_customer_care(prompt, user_id=user_id)
    }
    
@router.post('/bpo-interview/{user_id}', tags=["Interview"])
async def api_bpo_interview(input_data: TextInput, user_id: str):
    task = check_grammar(input_data.text)
    appreciateText = None
    if input_data.text.lower().strip('?.') == task.lower().strip('?.'):
        appreciateText = random.choice(appreciate_text)
    prompt = bpo_interview_prompt(input_data.text)
    return {
        "success": True,
        "appreciate_text": appreciateText,
        "text": input_data.text,
        "correct_text": task,
        "data": ai_bpo_interview(prompt, user_id=user_id)
    }

@router.post('/toefl-practice/{user_id}', tags=["TEST"])
async def api_toefl_practice(input_data: TextInput, user_id: str):
    corrected = check_grammar(input_data.text)
    appreciate = None
    if input_data.text.lower().strip('?.') == corrected.lower().strip('?.'):
        appreciate = random.choice(appreciate_text)
    prompt = toefl_prompt(input_data.text)
    response = ai_toefl_mentor(prompt, user_id)
    return {
        "success": True,
        "appreciate_text": appreciate,
        "text": input_data.text,
        "correct_text": corrected,
        "data": response
    }
    
@router.post('/ielts-practice/{user_id}', tags=["TEST"])
async def api_ielts_practice(input_data: TextInput, user_id: str):
    corrected = check_grammar(input_data.text)
    appreciate = None
    if input_data.text.lower().strip('?.') == corrected.lower().strip('?.'):
        appreciate = random.choice(appreciate_text)
    prompt = ielts_prompt(input_data.text)
    response = ai_ielts_mentor(prompt, user_id)
    return {
        "success": True,
        "appreciate_text": appreciate,
        "text": input_data.text,
        "correct_text": corrected,
        "data": response
    }

@router.post('/ai_report/{user_id}/{role}', tags=['user'])
async def api_ai_report(user_id,role):
    return {
        "success": True,
        "data": ai_report(user_id=user_id,role=role)
    }

@router.post('/reset-history_vinay/{user_id}/{convo_type}', tags=['AI-Tutor'])
async def reset_conversation_history(user_id: str, convo_type: str):
    reset_history(user_id=user_id, convo_type=convo_type)
    return {
        "success": True,
        "message": f"Conversation history for '{convo_type}' has been reset successfully."
    }
    