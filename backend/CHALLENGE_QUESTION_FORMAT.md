# Challenge Question Format Guide

## ✅ Fixed Issue

The validation has been updated to handle both object-style and simple array-style options.

---

## 📝 Correct Format for Multiple Choice Questions

### Options Field (Correct ✅)
```json
[
  {"label": "A", "text": "x: [1, 2, 3, 4], y: [1, 2, 3, 4], z: [1, 2, 3, 4, 5]"},
  {"label": "B", "text": "x: [99, 2, 3, 4], y: [99, 2, 3, 4], z: [1, 2, 3, 4, 5]"},
  {"label": "C", "text": "x: [99, 2, 3, 4, 6], y: [99, 2, 3, 4, 6], z: [1, 2, 3, 4, 5, 6]"},
  {"label": "D", "text": "x: [1, 2, 3, 4, 6], y: [1, 2, 3, 4, 6], z: [1, 2, 3, 4, 5]"}
]
```

### Correct Options Field

**IMPORTANT**: Use ONLY the labels, not the full objects!

**❌ WRONG** (What you had):
```json
[{"label": "A", "text": "x: [1, 2, 3, 4], y: [1, 2, 3, 4], z: [1, 2, 3, 4, 5]"}]
```

**✅ CORRECT** (What you should use):
```json
["A"]
```

Or for multiple correct answers:
```json
["A", "C"]
```

---

## 📋 Format for All Question Types

### 1. Single Choice

**Question Type**: `Single Choice`

**Options**:
```json
[
  {"label": "A", "text": "Option A text"},
  {"label": "B", "text": "Option B text"},
  {"label": "C", "text": "Option C text"}
]
```

**Correct Answer**: Just the label as a string
```
A
```

**Correct Options**: Leave empty `[]`

---

### 2. Multiple Choice (Your Case)

**Question Type**: `Multiple Choice`

**Options**:
```json
[
  {"label": "A", "text": "Option A text"},
  {"label": "B", "text": "Option B text"},
  {"label": "C", "text": "Option C text"}
]
```

**Correct Answer**: Leave empty

**Correct Options**: Array of labels only
```json
["A", "C"]
```

---

### 3. True/False

**Question Type**: `True / False`

**Options**: Leave empty `[]`

**Correct Answer**: 
```
true
```
or
```
false
```

**Correct Options**: Leave empty `[]`

---

### 4. Numeric

**Question Type**: `Numeric`

**Options**: Leave empty `[]`

**Correct Answer**: A number as text
```
42.5
```

**Numeric Tolerance**: How much deviation is allowed
```
0.1
```
(This means 42.4 to 42.6 would be accepted)

**Correct Options**: Leave empty `[]`

---

### 5. Short Text (Strict)

**Question Type**: `Short Text (Strict)`

**Options**: Leave empty `[]`

**Correct Answer**: The exact text expected
```
Python
```

**Correct Options**: Leave empty `[]`

---

## 🔧 How to Fix Your Current Question

Based on your screenshot:

### Change This:

**Correct options:**
```json
[{"label": "A", "text": "x: [1, 2, 3, 4], y: [1, 2, 3, 4], z: [1, 2, 3, 4, 5]"}]
```

### To This:

**Correct options:**
```json
["A"]
```

That's it! Just use the label string, not the whole object.

---

## 🎯 Quick Reference

| Question Type | Options Format | Correct Answer | Correct Options |
|---------------|----------------|----------------|-----------------|
| Single Choice | Array of `{"label": "X", "text": "..."}` | "A" | `[]` |
| Multiple Choice | Array of `{"label": "X", "text": "..."}` | Empty | `["A", "B"]` |
| True/False | `[]` | "true" or "false" | `[]` |
| Numeric | `[]` | "42.5" | `[]` |
| Short Text | `[]` | "Expected text" | `[]` |

---

## 💡 Pro Tips

1. **Labels should be short**: "A", "B", "C", "D" or "1", "2", "3", "4"
2. **Text can be long**: Full explanation goes in the "text" field
3. **For multiple correct answers**: Use array syntax `["A", "C", "D"]`
4. **JSON must be valid**: Use a JSON validator if unsure
5. **Explanation field**: Add detailed explanation for why the answer is correct

---

## 🚀 Now Try Again

1. Go back to your Django admin
2. Change the **Correct options** field to just: `["A"]`
3. Click Save
4. Should work now! ✅

---

## 🐛 Still Getting Errors?

Check the terminal where Django is running - it will show the exact validation error message.

Common issues:
- JSON syntax error (missing comma, quote, bracket)
- Label in correct_options doesn't match any label in options
- Empty fields that are required
