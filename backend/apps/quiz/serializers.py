from django.forms.models import model_to_dict


def serialize_quiz(quiz):
    return model_to_dict(quiz, fields=["id", "title", "description", "created_at", "updated_at"])


def serialize_question(question):
    return model_to_dict(question, fields=["id", "quiz", "prompt", "order", "created_at"])


def serialize_answer(answer):
    return model_to_dict(answer, fields=["id", "question", "text", "is_correct", "order"])