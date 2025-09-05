from app.core.settings import groq_client
from app.core.prompts import *
from app.core.harmful_content import contains_harmful_content
from app.core.db import *
from app.utils.helpers import *
import re
from difflib import SequenceMatcher
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

def translate_text(text: str, source_language: str, target_language: str) -> str:
    prompt = generic_translation_prompt(text, source_language, target_language)

    chat_completion = groq_client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="openai/gpt-oss-20b",
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
        input_country = (country_info.get("country_name") or "").strip()

        is_state = country_info.get("state") == "yes"
        input_state = (country_info.get("state_name") or "").strip()

        stored_country = load_user_country(user_id).strip().lower() if load_user_country(user_id) else None
        stored_state = load_user_state(user_id).strip().lower() if load_user_state(user_id) else None

        # If country is present and different or first-time, update
        if is_country and input_country.lower() != (stored_country or ""):
            save_user_country(user_id, input_country)

        # If state is present and different or first-time, update
        if is_state and input_state.lower() != (stored_state or ""):
            save_user_state(user_id, input_state)

        # Determine context: use most recent valid country/state
        final_country = input_country if is_country else load_user_country(user_id)
        final_state = input_state if is_state else load_user_state(user_id)

        if not final_country and not final_state:
            return "Hi there! Please mention a country or state to begin."

        # Construct context-aware prompt
        context_note = []
        if final_country:
            context_note.append(f"Country: {final_country}")
        if final_state:
            context_note.append(f"State: {final_state}")
        modified_prompt = f"{prompt} ({', '.join(context_note)})"

        return chat_with_memory(
            prompt=modified_prompt,
            user_id=user_id,
            role_key="country",
            system_prompt_func=lambda user_prompt: country_knowledge_prompt(user_prompt)
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

def ai_admin_interview(prompt: str, user_id: str) -> str:
    return chat_with_memory(
        prompt=prompt,
        user_id=user_id,
        role_key="admin_interview",
        system_prompt_func=admin_interview_prompt
    )

def ai_jre_interview(prompt: str, user_id: str) -> str:
    return chat_with_memory(
        prompt=prompt,
        user_id=user_id,
        role_key="jre_interview",
        system_prompt_func=jre_interview_prompt
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

def clean_corrected_output(text: str) -> str:
    return re.sub(r'^["\']|["\']$', '', text.strip())

# 3. Estimate errors using difflib (word-level difference)
def estimate_error_count(original: str, corrected: str) -> int:
    matcher = SequenceMatcher(None, original.strip().split(), corrected.strip().split())
    return len([op for op in matcher.get_opcodes() if op[0] != 'equal'])

# 4. Calculate accuracy based on error count and word count
def calculate_accuracy(original: str, error_count: int) -> str:
    words = len(original.strip().split())
    if words == 0:
        return "0%"
    accuracy = ((words - error_count) / words) * 100
    return f"{accuracy:.2f}%"

# 5. Main function: Get corrected text and compute accuracy
def image_description_grammar(text: str) -> dict:
    grammar_prompt = correct_grammar_for_image(text)

    # Call Groq API for corrected text
    grammar_correct_response = groq_client.chat.completions.create(
        messages=[{'role': 'system', 'content': grammar_prompt}],
        model=MODEL_NAME
    )
    corrected_text_raw = grammar_correct_response.choices[0].message.content
    corrected_text = clean_corrected_output(corrected_text_raw)

    # Compute actual error count and accuracy
    error_count = estimate_error_count(text, corrected_text)
    accuracy = calculate_accuracy(text, error_count)

    return {
        "original": text,
        "corrected": corrected_text,
        "accuracy": accuracy,
        "errors": str(error_count)
    }