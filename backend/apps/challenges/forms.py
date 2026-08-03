from django import forms
import json

from .models import ChallengeQuestion


class ChallengeQuestionAdminForm(forms.ModelForm):
    class Meta:
        model = ChallengeQuestion
        fields = '__all__'
        help_texts = {
            'options': 'For choice questions: [{"label": "A", "text": "Option A"}, {"label": "B", "text": "Option B"}]',
            'correct_options': 'For MULTIPLE choice: Use labels only like ["A"] or ["A", "B"]. NOT full objects!',
            'correct_answer': 'For SINGLE choice: Use label only like "A". For True/False: "true" or "false". For Numeric: a number.',
        }

    def clean_options(self):
        """Validate and clean the options field"""
        options = self.cleaned_data.get('options')
        
        if not options:
            return []
        
        # Ensure it's a list
        if not isinstance(options, list):
            raise forms.ValidationError('Options must be a JSON array.')
        
        # Validate each option has required fields
        for idx, opt in enumerate(options):
            if isinstance(opt, dict):
                if 'label' not in opt:
                    raise forms.ValidationError(f'Option {idx + 1} is missing "label" field.')
                if 'text' not in opt:
                    raise forms.ValidationError(f'Option {idx + 1} is missing "text" field.')
        
        return options

    def clean_correct_options(self):
        """Validate and clean the correct_options field"""
        correct_options = self.cleaned_data.get('correct_options')
        
        if not correct_options:
            return []
        
        # Ensure it's a list
        if not isinstance(correct_options, list):
            raise forms.ValidationError('Correct options must be a JSON array like ["A"] or ["A", "B"].')
        
        # Check if user mistakenly provided full objects
        if correct_options and isinstance(correct_options[0], dict):
            raise forms.ValidationError(
                'Correct options should be an array of labels like ["A"] or ["A", "B"], '
                'NOT full objects. You provided full objects. '
                'Just use the labels from your options.'
            )
        
        return correct_options

    def clean(self):
        cleaned_data = super().clean()

        try:
            question_type = cleaned_data.get('question_type')
            options = cleaned_data.get('options') or []
            correct_options = cleaned_data.get('correct_options') or []
            correct_answer = (cleaned_data.get('correct_answer') or '').strip()
            numeric_tolerance = cleaned_data.get('numeric_tolerance', 0)

            print("=" * 80)
            print("FORM CLEAN METHOD")
            print(f"Has challenge: {cleaned_data.get('challenge') is not None}")
            print(f"Has question_text: {bool(cleaned_data.get('question_text'))}")
            print(f"Form errors so far: {self.errors}")
            print("=" * 80)

            # Only validate if we have the necessary data
            if question_type in {ChallengeQuestion.TYPE_SINGLE_CHOICE, ChallengeQuestion.TYPE_MULTIPLE_CHOICE}:
                if not options:
                    self.add_error('options', 'Options are required for choice question types.')
                    return cleaned_data
                
                # Extract labels from options (they should be objects with 'label' field)
                option_labels = []
                for opt in options:
                    if isinstance(opt, dict) and 'label' in opt:
                        option_labels.append(opt['label'])
                    elif isinstance(opt, str):
                        option_labels.append(opt)
                
                if not option_labels:
                    self.add_error('options', 'Could not extract labels from options. Format: [{"label": "A", "text": "..."}]')
                    return cleaned_data

                # Validate SINGLE CHOICE
                if question_type == ChallengeQuestion.TYPE_SINGLE_CHOICE:
                    if not correct_answer:
                        self.add_error('correct_answer', 'Single choice requires a correct answer.')
                    elif correct_answer not in option_labels:
                        self.add_error('correct_answer', 
                            f'Correct answer "{correct_answer}" must be one of: {", ".join(option_labels)}')

                # Validate MULTIPLE CHOICE
                if question_type == ChallengeQuestion.TYPE_MULTIPLE_CHOICE:
                    if not correct_options:
                        self.add_error('correct_options', 
                            f'Multiple choice requires at least one correct option. '
                            f'Use labels like ["A"] or ["A", "B"]. Available: {", ".join(option_labels)}')
                    else:
                        # correct_options should already be cleaned (just labels, not objects)
                        invalid = [label for label in correct_options if label not in option_labels]
                        if invalid:
                            self.add_error('correct_options', 
                                f'Invalid labels: {", ".join(invalid)}. '
                                f'Must be from: {", ".join(option_labels)}. '
                                f'Format: ["A"] not [{{"label": "A", "text": "..."}}]')

            # Validate TRUE/FALSE
            if question_type == ChallengeQuestion.TYPE_TRUE_FALSE:
                if correct_answer.lower() not in {'true', 'false'}:
                    self.add_error('correct_answer', 'True/False requires correct_answer to be "true" or "false".')

            # Validate NUMERIC
            if question_type == ChallengeQuestion.TYPE_NUMERIC:
                try:
                    float(correct_answer)
                except (TypeError, ValueError):
                    self.add_error('correct_answer', 'Numeric questions require a numeric correct answer.')

                if numeric_tolerance is not None and numeric_tolerance < 0:
                    self.add_error('numeric_tolerance', 'Numeric tolerance must be >= 0.')

        except Exception as e:
            # Catch any unexpected errors and display them
            error_msg = f'Unexpected validation error: {str(e)}. Check terminal logs for details.'
            self.add_error(None, error_msg)
            print("=" * 80)
            print("FORM VALIDATION EXCEPTION:")
            print(error_msg)
            import traceback
            traceback.print_exc()
            print("=" * 80)

        print(f"Form errors after clean: {self.errors}")
        return cleaned_data
