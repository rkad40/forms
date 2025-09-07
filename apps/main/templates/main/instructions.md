To create a custom Boolean widget in Django that sets the field value to `True` **only if pressed**, you can subclass `forms.Widget` or `forms.CheckboxInput`, depending on your desired behavior. If you're aiming for something like a **"Confirm" button** or a **single-action toggle**, here's a clean way to do it.

---

## ✅ Goal
You want a widget that:
- Renders as a button or checkbox.
- Sets the field to `True` **only if the user interacts with it**.
- Defaults to `False` if untouched.

---

## 🛠️ Option 1: Custom Button Widget (e.g. "Confirm" or "Mark as True")

### 1. **Custom Widget**
```python
from django import forms

class ConfirmButtonWidget(forms.Widget):
    def render(self, name, value, attrs=None, renderer=None):
        final_attrs = self.build_attrs(attrs, name=name)
        return f'<button type="submit" name="{name}" value="true">Confirm</button>'

    def value_from_datadict(self, data, files, name):
        return data.get(name) == 'true'
```

### 2. **Form Field**
```python
class MyForm(forms.Form):
    confirmed = forms.BooleanField(required=False, widget=ConfirmButtonWidget())
```

### 🔍 Behavior
- If the button is pressed, `confirmed` will be `True`.
- If not pressed, it will be `False`.

---

## 🛠️ Option 2: Custom Checkbox That Always Sets True

If you want a checkbox that **only sets `True` when checked**, and never sends `False` explicitly:

```python
class OneWayCheckboxWidget(forms.CheckboxInput):
    def value_from_datadict(self, data, files, name):
        return bool(data.get(name))
```

This is similar to Django’s default behavior, but you can customize rendering or styling.

---

## 🧪 Testing in Template
```django
<form method="post">
  {% csrf_token %}
  {{ form.confirmed }}
</form>
```

Or if you want to manually render:
```django
<form method="post">
  <button type="submit" name="confirmed" value="true">Confirm</button>
</form>
```

---

Would you like this widget to look like a toggle switch, or integrate with JavaScript for more dynamic behavior? I can help style it or make it reusable across forms.
