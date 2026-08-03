# 📝 Sample Challenge Questions - Copy & Paste Ready

## 🎯 Multiple Choice Question

### Question Text:
```
What will be the output of the following Python code?

x = [1, 2, 3]
y = x
x.append(4)
print(y)
```

### Question Type:
```
Multiple Choice
```

### Options:
```json
[{"label": "A", "text": "[1, 2, 3]"}, {"label": "B", "text": "[1, 2, 3, 4]"}, {"label": "C", "text": "Error"}, {"label": "D", "text": "None"}]
```

### Correct Options:
```json
["B"]
```

### Correct Answer:
```
(Leave empty for multiple choice)
```

### Explanation:
```
Lists are mutable objects in Python. When y = x is executed, both variables reference the same list object. Therefore, modifying x also affects y.
```

---

## 🎯 Single Choice Question

### Question Text:
```
Which of the following is the correct syntax to create a dictionary in Python?
```

### Question Type:
```
Single Choice
```

### Options:
```json
[{"label": "A", "text": "dict = []"}, {"label": "B", "text": "dict = {}"}, {"label": "C", "text": "dict = ()"}, {"label": "D", "text": "dict = <>"}]
```

### Correct Options:
```json
[]
```

### Correct Answer:
```
B
```

### Explanation:
```
In Python, dictionaries are created using curly braces {}. Square brackets [] create lists, parentheses () create tuples, and <> is not valid syntax.
```

---

## 🎯 True/False Question

### Question Text:
```
In Python, strings are immutable objects.
```

### Question Type:
```
True / False
```

### Options:
```json
[]
```

### Correct Options:
```json
[]
```

### Correct Answer:
```
true
```

### Explanation:
```
True. Strings in Python are immutable, meaning once created, their content cannot be changed. Any operation that appears to modify a string actually creates a new string object.
```

---

## 🎯 Numeric Question

### Question Text:
```
What is the result of the expression: 15 // 4 in Python?
```

### Question Type:
```
Numeric
```

### Options:
```json
[]
```

### Correct Options:
```json
[]
```

### Correct Answer:
```
3
```

### Numeric Tolerance:
```
0
```

### Explanation:
```
The // operator performs floor division in Python, which returns the largest integer less than or equal to the division result. 15 // 4 = 3 (not 3.75).
```

---

## 🎯 Numeric Question with Tolerance

### Question Text:
```
Calculate the average of the following numbers: 10, 20, 30, 40, 50
```

### Question Type:
```
Numeric
```

### Options:
```json
[]
```

### Correct Options:
```json
[]
```

### Correct Answer:
```
30
```

### Numeric Tolerance:
```
0.5
```

### Explanation:
```
The average is calculated as (10 + 20 + 30 + 40 + 50) / 5 = 150 / 5 = 30. Answers between 29.5 and 30.5 are accepted due to tolerance.
```

---

## 🎯 Short Text (Strict) Question

### Question Text:
```
What keyword is used to define a function in Python?
```

### Question Type:
```
Short Text (Strict)
```

### Options:
```json
[]
```

### Correct Options:
```json
[]
```

### Correct Answer:
```
def
```

### Explanation:
```
The 'def' keyword is used to define functions in Python. It stands for "define" and is followed by the function name and parameters.
```

---

## 🎯 Multiple Choice with Multiple Correct Answers

### Question Text:
```
Which of the following are valid Python data types? (Select all that apply)
```

### Question Type:
```
Multiple Choice
```

### Options:
```json
[{"label": "A", "text": "int"}, {"label": "B", "text": "float"}, {"label": "C", "text": "string"}, {"label": "D", "text": "boolean"}]
```

### Correct Options:
```json
["A", "B"]
```

### Correct Answer:
```
(Leave empty for multiple choice)
```

### Explanation:
```
int and float are valid Python data types. While 'string' and 'boolean' are concepts in Python, the actual type names are 'str' and 'bool'.
```

---

## 🎯 Your Python Variable Question (Fixed)

### Question Text:
```
What are the values of x, y, and z after executing the following code?

x = [1, 2, 3]
y = x
x += [4]
z = x + [5]

def modify(lst):
    lst = lst + [6]
    lst[0] = 99

modify(y)
```

### Question Type:
```
Multiple Choice
```

### Options:
```json
[{"label": "A", "text": "x: [1, 2, 3, 4], y: [1, 2, 3, 4], z: [1, 2, 3, 4, 5]"}, {"label": "B", "text": "x: [99, 2, 3, 4], y: [99, 2, 3, 4], z: [1, 2, 3, 4, 5]"}, {"label": "C", "text": "x: [99, 2, 3, 4, 6], y: [99, 2, 3, 4, 6], z: [1, 2, 3, 4, 5, 6]"}, {"label": "D", "text": "x: [1, 2, 3, 4, 6], y: [1, 2, 3, 4, 6], z: [1, 2, 3, 4, 5]"}]
```

### Correct Options:
```json
["A"]
```

### Correct Answer:
```
(Leave empty for multiple choice)
```

### Explanation:
```
1. x += [4] mutates the original list in-place, so both x and y reference [1, 2, 3, 4].
2. z = x + [5] creates a new list [1, 2, 3, 4, 5].
3. Inside modify(lst), lst = lst + [6] creates a new local list, so modifying lst[0] = 99 affects only that local copy and leaves x and y unchanged.
```

---

## 📋 Quick Reference Table

| Field | Multiple Choice | Single Choice | True/False | Numeric | Short Text |
|-------|----------------|---------------|------------|---------|------------|
| **Options** | `[{"label": "A", "text": "..."}]` | `[{"label": "A", "text": "..."}]` | `[]` | `[]` | `[]` |
| **Correct Options** | `["A"]` or `["A", "B"]` | `[]` | `[]` | `[]` | `[]` |
| **Correct Answer** | Empty | `"A"` | `"true"` or `"false"` | `"42"` | `"def"` |

---

## 🎯 Pro Tips

1. **Labels**: Use simple labels like "A", "B", "C", "D" or "1", "2", "3", "4"
2. **Text**: Can be as long as needed, including code blocks
3. **JSON Format**: Make sure JSON is valid - use a JSON validator if unsure
4. **Multiple Correct**: For multiple choice with several correct answers: `["A", "C", "D"]`
5. **Explanations**: Always provide detailed explanations for learning purposes

---

## 🚀 Copy-Paste Workflow

1. Copy the entire section for your question type
2. Paste into Django admin fields one by one
3. Modify the content to match your question
4. Save!

---

## ⚠️ Common Mistakes to Avoid

❌ **WRONG**: `{"label": "A", "text": "..."}` in Correct Options
✅ **RIGHT**: `["A"]` in Correct Options

❌ **WRONG**: Forgetting quotes around labels: `[A]`
✅ **RIGHT**: Quotes around labels: `["A"]`

❌ **WRONG**: Using comma at the end of JSON array: `["A",]`
✅ **RIGHT**: No trailing comma: `["A"]`

---

## 🔧 Validation Checklist

Before saving, check:
- [ ] Question text is clear and complete
- [ ] Question type is selected
- [ ] For choice questions: Options are formatted correctly
- [ ] For multiple choice: Correct options uses labels only `["A"]`
- [ ] For single choice: Correct answer uses label only `"A"`
- [ ] For true/false: Correct answer is `"true"` or `"false"`
- [ ] For numeric: Correct answer is a number as text `"42"`
- [ ] Explanation is provided
- [ ] Order field is set (for question sequence)

---

## 🎉 Ready to Use!

Pick any sample above and paste it directly into Django admin. Just modify the content to match your needs!
