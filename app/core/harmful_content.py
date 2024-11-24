harmful_keywords = [
     "abuse", "hate", "violence", "racism", "sex", "rape", "discrimination", 
    "offensive", "harassment", "fuck"
]

appreciate_text = ['Great Job!', 'Excellent work!', 'Well done!', 'Awesome job!', 'Fantastic effort!', 'You nailed it!', 'Superb performance!', 'Outstanding work!', 'Nice going!', 'You did amazing!', 'Excellent effort!', 'Keep it up!']

def contains_harmful_content(text: str) -> bool:
    return any(keyword in text.lower() for keyword in harmful_keywords)