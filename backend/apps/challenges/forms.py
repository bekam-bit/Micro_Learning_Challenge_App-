from django import forms

from .models import ChallengeQuestion


class ChallengeQuestionAdminForm(forms.ModelForm):
    class Meta:
        model = ChallengeQuestion
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()

        question_type = cleaned_data.get('question_type')
        options = cleaned_data.get('options') or []
        correct_options = cleaned_data.get('correct_options') or []
        correct_answer = (cleaned_data.get('correct_answer') or '').strip()
        numeric_tolerance = cleaned_data.get('numeric_tolerance', 0)

        if question_type in {ChallengeQuestion.TYPE_SINGLE_CHOICE, ChallengeQuestion.TYPE_MULTIPLE_CHOICE} and not options:
            self.add_error('options', 'Options are required for choice question types.')

        if question_type == ChallengeQuestion.TYPE_SINGLE_CHOICE:
            if not correct_answer:
                self.add_error('correct_answer', 'Single choice requires a correct answer.')
            elif correct_answer not in options:
                self.add_error('correct_answer', 'Correct answer must be one of the available options.')

        if question_type == ChallengeQuestion.TYPE_MULTIPLE_CHOICE:
            if not correct_options:
                self.add_error('correct_options', 'Multiple choice requires at least one correct option.')
            else:
                invalid = [value for value in correct_options if value not in options]
                if invalid:
                    self.add_error('correct_options', 'Each correct option must exist in options.')

        if question_type == ChallengeQuestion.TYPE_TRUE_FALSE:
            if correct_answer.lower() not in {'true', 'false'}:
                self.add_error('correct_answer', 'True/False requires correct_answer to be true or false.')

        if question_type == ChallengeQuestion.TYPE_NUMERIC:
            try:
                float(correct_answer)
            except (TypeError, ValueError):
                self.add_error('correct_answer', 'Numeric questions require a numeric correct answer.')

            if numeric_tolerance is not None and numeric_tolerance < 0:
                self.add_error('numeric_tolerance', 'Numeric tolerance must be greater than or equal to zero.')

        return cleaned_data
