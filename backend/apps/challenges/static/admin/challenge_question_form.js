(function () {
  function toggleRow(fieldName, isVisible) {
    var selector = '.form-row.field-' + fieldName + ', .field-' + fieldName;
    var row = document.querySelector(selector);
    if (!row) {
      return;
    }
    row.style.display = isVisible ? '' : 'none';
  }

  function applyTypeRules() {
    var select = document.getElementById('id_question_type');
    if (!select) {
      return;
    }

    var questionType = select.value;

    var showOptions = questionType === 'single_choice' || questionType === 'multiple_choice';
    var showCorrectOptions = questionType === 'multiple_choice';
    var showCorrectAnswer = questionType !== 'multiple_choice';
    var showNumericTolerance = questionType === 'numeric';

    toggleRow('options', showOptions);
    toggleRow('correct_options', showCorrectOptions);
    toggleRow('correct_answer', showCorrectAnswer);
    toggleRow('numeric_tolerance', showNumericTolerance);
  }

  document.addEventListener('DOMContentLoaded', function () {
    var select = document.getElementById('id_question_type');
    if (!select) {
      return;
    }

    applyTypeRules();
    select.addEventListener('change', applyTypeRules);
  });
})();
