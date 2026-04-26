import random

def generate_math_captcha(request):
    """Generate a random math question and store the answer in the session."""
    num1 = random.randint(1, 10)
    num2 = random.randint(1, 10)
    request.session['captcha_answer'] = num1 + num2
    return f"{num1} + {num2}"

def validate_math_captcha(request, user_answer):
    """Validate the user's answer against the stored answer in the session."""
    correct_answer = request.session.get('captcha_answer')
    if correct_answer is None:
        return False
    try:
        if int(user_answer) == int(correct_answer):
            # Clear the answer after successful validation
            del request.session['captcha_answer']
            return True
    except (ValueError, TypeError):
        pass
    return False
