from app.core.settings import groq_client
from app.core.prompts import *
from app.core.harmful_content import contains_harmful_content
from app.core.db import *
from app.utils.helpers import *

MODEL_NAME = os.getenv('MODEL_NAME')
# Global variable to store the conversation history
user_conversations = {}

def check_grammar(text: str) -> str:
    grammar_prompt = grammar_prompts(text=text)
    chat_completion = groq_client.chat.completions.create(
        messages=[{'role':'system', 'content':grammar_prompt}],
        model=MODEL_NAME
    )

    return chat_completion.choices[0].message.content.strip()

def translate_text(text: str) -> str: 
    translation_text = hindi_to_english_translation_prompts(text=text)
    chat_completion = groq_client.chat.completions.create(
        messages=[{'role':'user', 'content':translation_text}],
        model=MODEL_NAME
    )
    return chat_completion.choices[0].message.content.strip()


def idiom_text(text: str) -> str:
    hindi_to_english_idiom = hindi_idiom_to_english_prompt(text=text)
    chat_completion = groq_client.chat.completions.create(
        messages=[{'role':'user', 'content':hindi_to_english_idiom}],
        model=MODEL_NAME
    )
    return chat_completion.choices[0].message.content.strip()

def translate_text_to_hindi(text: str) -> str:
    translation_text = english_to_hindi_translation_prompt(text=text)
    chat_completion = groq_client.chat.completions.create(
        messages=[{'role': 'user', 'content': translation_text}],
        model=MODEL_NAME
    )
    return chat_completion.choices[0].message.content.strip()

def translate_text_to_language(text: str, target_language: str) -> str:
    prompt = english_to_target_language_prompt(text=text, target_language=target_language)
    
    chat_completion = groq_client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model=MODEL_NAME,
        temperature=0
    )

    return chat_completion.choices[0].message.content.strip()



# def ai_tutor(prompt: str, user_id: str) -> str:

    # convo = [{'role': 'system', 'content': sys_msg_prompts()}]
    key = f"{user_id}_tutor"

    if contains_harmful_content(prompt):
        return (
            "I'm sorry, but I cannot respond to harmful or inappropriate content. "
            "I am designed to assist with improving communication skills, providing advice, and enhancing grammar and vocabulary. "
            "Please keep the conversation respectful and focused on these topics."
        )
    # Retrieve or initialize conversation history for the user
    if key not in user_conversations:
        user_conversations[key] = [{'role': 'system', 'content': sys_msg_prompts()}]

     # Append user input to conversation history
    user_conversations[key].append({'role': 'user', 'content': prompt})

    # convo.append({'role':'user', 'content': prompt})
    chat_completion = groq_client.chat.completions.create(
        messages=user_conversations[key],
        model=MODEL_NAME
    )
    response = chat_completion.choices[0].message
    # convo.append(response)
    user_conversations[key].append(response)
    return response.content

def ai_tutor(prompt: str, user_id: str, new_chat: bool = False) -> str:
    return chat_with_memory(
        prompt=prompt,
        user_id=user_id,
        role_key="tutor",
        system_prompt_func=sys_msg_prompts,
        new_chat=new_chat
    )


def ai_interviewer(prompt: str, user_id: str) -> str:
    return chat_with_memory(
        prompt=prompt,
        user_id=user_id,
        role_key="interviewer",
        system_prompt_func=ai_interviewer_prompts
    )
    


def reset_history(user_id: str, convo_type: str):
    key = f"{user_id}_{convo_type}"  # Generate the correct key based on user ID and conversation type
    if key in user_conversations:
        # Reset the conversation history for the specific conversation type
        if convo_type == "interviewer":
            user_conversations[key] = [
                {'role': 'system', 'content': ai_interviewer_prompts()}
            ]
        elif convo_type == "tutor":
            user_conversations[key] = [
                {'role': 'system', 'content': sys_msg_prompts()}
            ]
        return True
    return False


def check_pronunciation(text: str) -> str:
    pro_prompt = pronunciation_prompt(text=text)

    chat_completion = groq_client.chat.completions.create(
        messages=[{'role': 'system', 'content': pro_prompt}],
        model=MODEL_NAME
    )

    return chat_completion.choices[0].message.content.strip()

# daily_routine_task
def daily_routine_task(prompt:str,user_id:str)->str:
    print(prompt)
    return chat_with_memory(
        prompt=prompt,
        user_id=user_id,
        role_key="routing",
        system_prompt_func=daily_routing_prompt
    )
    
def ai_hobbies_response(prompt: str, user_id: str) -> str:
    return chat_with_memory(
        prompt=prompt,
        user_id=user_id,
        role_key="hobbies",
        system_prompt_func=hobbies_prompt
    )
    
def about_country(prompt: str, user_id: str) -> str:
    try:
        country_info = is_country_name(prompt, MODEL_NAME)
        is_country = country_info.get("country") == "yes"
        input_country = (country_info.get("name") or "").strip()

        if is_country:
            stored_country = load_user_country(user_id).strip().lower() if load_user_country(user_id) else None
            # First-time or country changed — save new country
            if input_country.lower() != stored_country:
                save_user_country(user_id, input_country)
            return chat_with_memory(
                prompt=prompt,
                user_id=user_id,
                role_key="country",
                system_prompt_func=lambda user_prompt: country_knowledge_prompt(user_prompt, input_country)
            )

        else:
            stored_country = load_user_country(user_id)
            if not stored_country:
                return "Hi there! Please enter a valid country name to get started."

            modified_prompt = f"User Input : {prompt}, Current Country : {stored_country})"
            return chat_with_memory(
                prompt=modified_prompt,
                user_id=user_id,
                role_key="country",
                system_prompt_func=lambda user_prompt: country_knowledge_prompt(modified_prompt, stored_country)
            )

    except Exception as ex:
        print("ERROR in COUNTRY API: ", ex)
        return "Oops! Something went wrong while processing your request."


def ai_role_model(prompt:str,user_id:str)->str:
    return chat_with_memory(
        prompt=prompt,
        user_id=user_id,
        role_key="role_model",
        system_prompt_func=role_model_prompt
    )
    
def ai_social_media(prompt:str,user_id:str)->str:
    return chat_with_memory(
        prompt=prompt,
        user_id=user_id,
        role_key="social_media",
        system_prompt_func=social_media_prompt
    )

def ai_childhood_memory(prompt:str,user_id:str)->str:
    return chat_with_memory(
        prompt=prompt,
        user_id=user_id,
        role_key="childhood_memory",
        system_prompt_func=childhood_memory_prompt
    )
    
def ai_hr_interview(prompt:str,user_id:str)->str:
    return chat_with_memory(
        prompt=prompt,
        user_id=user_id,
        role_key="hr_interview",
        system_prompt_func=hr_interview_prompt
    )

def ai_government_job(prompt: str, user_id: str) -> str:
    return chat_with_memory(
        prompt=prompt,
        user_id=user_id,
        role_key="gov_job",
        system_prompt_func=government_job_prompt
    )
    
def ai_customer_care(prompt: str, user_id: str) -> str:
    return chat_with_memory(
        prompt=prompt,
        user_id=user_id,
        role_key="customer_care",
        system_prompt_func=customer_care_prompt
    )
    
def ai_bpo_interview(prompt: str, user_id: str) -> str:
    return chat_with_memory(
        prompt=prompt,
        user_id=user_id,
        role_key="bpo_interview",
        system_prompt_func=bpo_interview_prompt
    )
    
def ai_toefl_mentor(prompt: str, user_id: str) -> str:
    return chat_with_memory(
        prompt=prompt,
        user_id=user_id,
        role_key="toefl_mentor",
        system_prompt_func=toefl_prompt
    )
    
def ai_ielts_mentor(prompt: str, user_id: str) -> str:
    return chat_with_memory(
        prompt=prompt,
        user_id=user_id,
        role_key="ielts_mentor",
        system_prompt_func=ielts_prompt
    )

def ai_report(user_id: str,role: str) -> str:
    return conversation_report(
        user_id=user_id,
        role_key=role,
        system_prompt_func=conversation_scoring_prompt
    )