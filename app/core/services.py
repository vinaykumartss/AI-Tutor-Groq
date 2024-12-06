from app.core.settings import groq_client
from app.core.prompts import grammar_prompts, sys_msg_prompts, hindi_to_english_translation_prompts, hindi_idiom_to_english_prompt, ai_interviewer_prompts
from app.core.harmful_content import contains_harmful_content

# Global variable to store the conversation history
user_conversations = {}

def check_grammar(text: str) -> str:
    grammar_prompt = grammar_prompts(text=text)
    chat_completion = groq_client.chat.completions.create(
        messages=[{'role':'system', 'content':grammar_prompt}],
        model='llama3-70b-8192'
    )

    return chat_completion.choices[0].message.content.strip()

def translate_text(text: str) -> str: 
    translation_text = hindi_to_english_translation_prompts(text=text)
    chat_completion = groq_client.chat.completions.create(
        messages=[{'role':'user', 'content':translation_text}],
        model='llama3-70b-8192'
    )
    return chat_completion.choices[0].message.content.strip()

def idiom_text(text: str) -> str:
    hindi_to_english_idiom = hindi_idiom_to_english_prompt(text=text)
    chat_completion = groq_client.chat.completions.create(
        messages=[{'role':'user', 'content':hindi_to_english_idiom}],
        model='llama3-70b-8192'
    )
    return chat_completion.choices[0].message.content.strip()

def ai_tutor(prompt: str, user_id: str) -> str:

    # convo = [{'role': 'system', 'content': sys_msg_prompts()}]

    if contains_harmful_content(prompt):
        return (
            "I'm sorry, but I cannot respond to harmful or inappropriate content. "
            "I am designed to assist with improving communication skills, providing advice, and enhancing grammar and vocabulary. "
            "Please keep the conversation respectful and focused on these topics."
        )
    # Retrieve or initialize conversation history for the user
    if user_id not in user_conversations: 
        user_conversations[user_id] = [{'role': 'system', 'content': sys_msg_prompts()}]

     # Append user input to conversation history
    user_conversations[user_id].append({'role': 'user', 'content': prompt})

    # convo.append({'role':'user', 'content': prompt})
    chat_completion = groq_client.chat.completions.create(
        messages=user_conversations[user_id],
        model='llama3-70b-8192'
    )
    response = chat_completion.choices[0].message
    # convo.append(response)
    user_conversations[user_id].append(response)
    return response.content

def ai_interviewer(prompt: str, user_id: str) -> str:

    # Retrieve or initialize conversation history for the user
    if user_id not in user_conversations: 
        user_conversations[user_id] = [{'role': 'system', 'content': ai_interviewer_prompts()}]

     # Append user input to conversation history
    user_conversations[user_id].append({'role': 'user', 'content': prompt})

    # convo.append({'role':'user', 'content': prompt})
    chat_completion = groq_client.chat.completions.create(
        messages=user_conversations[user_id],
        model='llama3-70b-8192'
    )
    response = chat_completion.choices[0].message
    # convo.append(response)
    user_conversations[user_id].append(response)
    return response.content

def reset_history(user_id: str):
    if user_id in user_conversations:
        user_conversations[user_id] =[{'role': 'system', 'content': sys_msg_prompts()}]
        return True
    # conversation_history = [{'role': 'system', 'content': sys_msg_prompts()}]
    return False

def reset_history(user_id: str):
    if user_id in user_conversations:
        user_conversations[user_id] =[{'role': 'system', 'content': ai_interviewer_prompts()}]
        return True
    # conversation_history = [{'role': 'system', 'content': sys_msg_prompts()}]
    return False