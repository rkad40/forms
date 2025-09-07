from django import forms
import ocia_participant.models as m
import re
from rex import Rex

from django import forms

class OCIAParticipantLoginForm(forms.Form):
    email = forms.EmailField(label="Email", max_length=254)

'''
   ___   ____ ___    _      ____            _   _      _                   _   
  / _ \ / ___|_ _|  / \    |  _ \ __ _ _ __| |_(_) ___(_)_ __   __ _ _ __ | |_ 
 | | | | |    | |  / _ \   | |_) / _` | '__| __| |/ __| | '_ \ / _` | '_ \| __|
 | |_| | |___ | | / ___ \  |  __/ (_| | |  | |_| | (__| | |_) | (_| | | | | |_ 
  \___/ \____|___/_/   \_\ |_|   \__,_|_|   \__|_|\___|_| .__/ \__,_|_| |_|\__|
  _____                      __  __ _      _            |_|                    
 |  ___|__  _ __ _ __ ___   |  \/  (_)_  _(_)_ __                              
 | |_ / _ \| '__| '_ ` _ \  | |\/| | \ \/ / | '_ \                             
 |  _| (_) | |  | | | | | | | |  | | |>  <| | | | |                            
 |_|  \___/|_|  |_| |_| |_| |_|  |_|_/_/\_\_|_| |_|                            
                                                                               
'''

class OCIAParticipantFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.RadioSelect):
                # $$$ Replace choices to avoid Django injecting the empty "---------" label
                model_field = self._meta.model._meta.get_field(field_name)
                if hasattr(model_field, 'choices') and model_field.choices:
                    field.choices = [
                        (choice[0], choice[1]) for choice in model_field.choices
                    ]

'''
   ___   ____ ___    _      ____            _   _      _                   _   
  / _ \ / ___|_ _|  / \    |  _ \ __ _ _ __| |_(_) ___(_)_ __   __ _ _ __ | |_ 
 | | | | |    | |  / _ \   | |_) / _` | '__| __| |/ __| | '_ \ / _` | '_ \| __|
 | |_| | |___ | | / ___ \  |  __/ (_| | |  | |_| | (__| | |_) | (_| | | | | |_ 
  \___/ \____|___/_/   \_\ |_|   \__,_|_|   \__|_|\___|_| .__/ \__,_|_| |_|\__|
  _____                                                 |_|                    
 |  ___|__  _ __ _ __ ___                                                      
 | |_ / _ \| '__| '_ ` _ \                                                     
 |  _| (_) | |  | | | | | |                                                    
 |_|  \___/|_|  |_| |_| |_|                                                    
'''

class OCIAParticipantForm(OCIAParticipantFormMixin, forms.ModelForm):
    class Meta:
        model = m.OCIAParticipant
        # fields = "__all__"
        exclude = ['liturgical_year', 'created_on']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={ 'class': 'flatpickr', 'placeholder': 'Select a date', 'type': 'text'}), 
            'can_text': forms.RadioSelect(choices=m.YesNoChoices),
            'sex': forms.RadioSelect(choices=m.SexChoices),
            'marital_status': forms.RadioSelect(choices=m.MaritalStatusChoices),
            'engaged': forms.RadioSelect(choices=m.YesNoChoices),
        }
    
    def clean_first_name(self):
        value = str(self.cleaned_data["first_name"]).strip()
        if value == '': raise forms.ValidationError("⚠ First name must be defined.")
        return value
    
    def clean_last_name(self):
        value = str(self.cleaned_data["last_name"]).strip()
        if value == '': raise forms.ValidationError("⚠ Last name must be defined.")
        return value
    
    def clean_email(self):
        value = str(self.cleaned_data["email"]).strip()
        if value == '': raise forms.ValidationError("⚠ Email must be defined.")
        pattern = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
        if pattern.match(value) is None: raise forms.ValidationError("⚠ Not a valid email.")
        return value

    def clean_phone(self):
        value = str(self.cleaned_data["phone"]).strip()
        if value == '': return value
        pattern = re.compile(r"^(?:\+1\s?)?(?:\(?\d{3}\)?[\s.-]?)?\d{3}[\s.-]?\d{4}$")
        if pattern.match(value) is None: raise forms.ValidationError("⚠ Not a valid phone number. Phone numbers must be 10 digits and match one of: ##########, (###) ###-####, ###.###.####, ###-###-####.")
        digits = re.sub(r"\D", "", value)
        if len(digits) == 11 and digits.startswith("1"): digits = digits[1:]
        if len(digits) != 10: forms.ValidationError(f"⚠ Not a valid phone number. Value {value} has {len(digits)} digits. It must have exactly 10 digits.")
        value = f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        self.data = self.data.copy()
        self.data["phone"] = value
        return value

    def clean_num_marriages(self):
        value = str(self.cleaned_data["num_marriages"]).strip()
        if value == '':
            raise forms.ValidationError("⚠ Number of marriages cannot be blank.")
        try: 
            value = int(self.cleaned_data["num_marriages"])
        except: 
            raise forms.ValidationError("⚠ Number of marriages must be a number.")
        if value < 0:
            raise forms.ValidationError("⚠ Number of marriages cannot be negative.")
        return value
    
    def clean_engaged(self):
        marital_status = str(self.cleaned_data["marital_status"]).strip()
        value = str(self.cleaned_data["engaged"]).strip()
        if marital_status == 'single' and value == '':
            raise forms.ValidationError("⚠ If not married, please indicate if you are engaged to be married.")
        return value
    
'''
   ___   ____ ___    _      ____            _   _      _                   _   
  / _ \ / ___|_ _|  / \    |  _ \ __ _ _ __| |_(_) ___(_)_ __   __ _ _ __ | |_ 
 | | | | |    | |  / _ \   | |_) / _` | '__| __| |/ __| | '_ \ / _` | '_ \| __|
 | |_| | |___ | | / ___ \  |  __/ (_| | |  | |_| | (__| | |_) | (_| | | | | |_ 
  \___/ \____|___/_/   \_\ |_|   \__,_|_|   \__|_|\___|_| .__/ \__,_|_| |_|\__|
  __  __                 _                    _____     |_|                    
 |  \/  | __ _ _ __ _ __(_) __ _  __ _  ___  |  ___|__  _ __ _ __ ___          
 | |\/| |/ _` | '__| '__| |/ _` |/ _` |/ _ \ | |_ / _ \| '__| '_ ` _ \         
 | |  | | (_| | |  | |  | | (_| | (_| |  __/ |  _| (_) | |  | | | | | |        
 |_|  |_|\__,_|_|  |_|  |_|\__,_|\__, |\___| |_|  \___/|_|  |_| |_| |_|        
                                 |___/                                         
'''

class OCIAParticipantMarriageForm(OCIAParticipantFormMixin, forms.ModelForm):
    class Meta:
        model = m.OCIAParticipantMarriage
        exclude = ["participant", "admin_notes"]
        widgets = {
            'date_of_marriage': forms.DateInput(attrs={ 'class': 'flatpickr', 'placeholder': 'Select a date', 'type': 'text'}), 
            'date_of_divorce': forms.DateInput(attrs={ 'class': 'flatpickr', 'placeholder': 'Select a date', 'type': 'text'}), 
            'status': forms.RadioSelect(choices=m.MarriageStatusChoices),
            'spouse_first_marriage': forms.RadioSelect(choices=m.YesNoChoices),
            'marital_status': forms.RadioSelect(choices=m.MaritalStatusChoices),
        }

'''
   ___   ____ ___    _      ____            _   _      _                   _   
  / _ \ / ___|_ _|  / \    |  _ \ __ _ _ __| |_(_) ___(_)_ __   __ _ _ __ | |_ 
 | | | | |    | |  / _ \   | |_) / _` | '__| __| |/ __| | '_ \ / _` | '_ \| __|
 | |_| | |___ | | / ___ \  |  __/ (_| | |  | |_| | (__| | |_) | (_| | | | | |_ 
  \___/ \____|___/_/   \_\ |_|   \__,_|_|   \__|_|\___|_| .__/ \__,_|_| |_|\__|
  ____      _ _       _               _____             |_|                    
 |  _ \ ___| (_) __ _(_) ___  _ __   |  ___|__  _ __ _ __ ___                  
 | |_) / _ \ | |/ _` | |/ _ \| '_ \  | |_ / _ \| '__| '_ ` _ \                 
 |  _ <  __/ | | (_| | | (_) | | | | |  _| (_) | |  | | | | | |                
 |_| \_\___|_|_|\__, |_|\___/|_| |_| |_|  \___/|_|  |_| |_| |_|                
                |___/                                                          
'''

class OCIAParticipantReligionForm(OCIAParticipantFormMixin, forms.ModelForm):
    class Meta:
        model = m.OCIAParticipantReligion
        exclude = ["participant", "admin_notes"]
        widgets = {
            'affiliation': forms.RadioSelect(choices=m.ReligionChoices),
            'baptized': forms.RadioSelect(choices=m.UnknownChoices),
            'sacrament_of_confession': forms.RadioSelect(choices=m.UnknownChoices),
            'sacrament_of_communion': forms.RadioSelect(choices=m.UnknownChoices),
            'sacrament_of_confirmation': forms.RadioSelect(choices=m.UnknownChoices),
            'baptized_denomination': forms.RadioSelect(choices=m.DenominationChoices),
            'baptized_on': forms.DateInput(attrs={ 'class': 'flatpickr', 'placeholder': 'Select a date', 'type': 'text'}), 
        }

'''
   ___   ____ ___    _      ____            _   _      _                   _   
  / _ \ / ___|_ _|  / \    |  _ \ __ _ _ __| |_(_) ___(_)_ __   __ _ _ __ | |_ 
 | | | | |    | |  / _ \   | |_) / _` | '__| __| |/ __| | '_ \ / _` | '_ \| __|
 | |_| | |___ | | / ___ \  |  __/ (_| | |  | |_| | (__| | |_) | (_| | | | | |_ 
  \___/ \____|___/_/   \_\ |_|   \__,_|_|   \__|_|\___|_| .__/ \__,_|_| |_|\__|
  ____                      _     _____                 |_|                    
 |  _ \ __ _ _ __ ___ _ __ | |_  |  ___|__  _ __ _ __ ___                      
 | |_) / _` | '__/ _ \ '_ \| __| | |_ / _ \| '__| '_ ` _ \                     
 |  __/ (_| | | |  __/ | | | |_  |  _| (_) | |  | | | | | |                    
 |_|   \__,_|_|  \___|_| |_|\__| |_|  \___/|_|  |_| |_| |_|                    
                                                                               
'''

class OCIAParticipantParentForm(OCIAParticipantFormMixin, forms.ModelForm):
    class Meta:
        model = m.OCIAParticipantParent
        exclude = ["participant"]
        widgets = {
            'relationship': forms.RadioSelect(choices=m.ParentTitleChoices),
        }

'''
   ___   ____ ___    _      ____            _   _      _                   _             
  / _ \ / ___|_ _|  / \    |  _ \ __ _ _ __| |_(_) ___(_)_ __   __ _ _ __ | |_           
 | | | | |    | |  / _ \   | |_) / _` | '__| __| |/ __| | '_ \ / _` | '_ \| __|          
 | |_| | |___ | | / ___ \  |  __/ (_| | |  | |_| | (__| | |_) | (_| | | | | |_           
  \___/ \____|___/_/   \_\ |_|   \__,_|_|   \__|_|\___|_| .__/ \__,_|_| |_|\__|          
  _____                                                 |_|     _____                    
 | ____|_ __   __ _  __ _  __ _  ___ _ __ ___   ___ _ __ | |_  |  ___|__  _ __ _ __ ___  
 |  _| | '_ \ / _` |/ _` |/ _` |/ _ \ '_ ` _ \ / _ \ '_ \| __| | |_ / _ \| '__| '_ ` _ \ 
 | |___| | | | (_| | (_| | (_| |  __/ | | | | |  __/ | | | |_  |  _| (_) | |  | | | | | |
 |_____|_| |_|\__, |\__,_|\__, |\___|_| |_| |_|\___|_| |_|\__| |_|  \___/|_|  |_| |_| |_|
              |___/       |___/                                                          
'''

class OCIAParticipantEngagementForm(OCIAParticipantFormMixin, forms.ModelForm):
    class Meta:
        model = m.OCIAParticipantEngagement
        exclude = ["participant", "admin_notes"]
        widgets = {
            'fiance_first_marriage': forms.RadioSelect(choices=m.UnknownChoices),
            'your_first_marriage': forms.RadioSelect(choices=m.YesNoChoices),
            'planned_date_of_marriage': forms.DateInput(attrs={ 'class': 'flatpickr', 'placeholder': 'Select a date', 'type': 'text'}), 
        }

'''
   ___   ____ ___    _      ____            _   _      _                   _   
  / _ \ / ___|_ _|  / \    |  _ \ __ _ _ __| |_(_) ___(_)_ __   __ _ _ __ | |_ 
 | | | | |    | |  / _ \   | |_) / _` | '__| __| |/ __| | '_ \ / _` | '_ \| __|
 | |_| | |___ | | / ___ \  |  __/ (_| | |  | |_| | (__| | |_) | (_| | | | | |_ 
  \___/ \____|___/_/   \_\ |_|   \__,_|_|   \__|_|\___|_| .__/ \__,_|_| |_|\__|
   ___                  _   _                   _____   |_|                    
  / _ \ _   _  ___  ___| |_(_) ___  _ __  ___  |  ___|__  _ __ _ __ ___        
 | | | | | | |/ _ \/ __| __| |/ _ \| '_ \/ __| | |_ / _ \| '__| '_ ` _ \       
 | |_| | |_| |  __/\__ \ |_| | (_) | | | \__ \ |  _| (_) | |  | | | | | |      
  \__\_\\__,_|\___||___/\__|_|\___/|_| |_|___/ |_|  \___/|_|  |_| |_| |_|      
                                                                                                                                                              
'''

class OCIAParticipantQuestionsForm(OCIAParticipantFormMixin, forms.ModelForm):
    class Meta:
        model = m.OCIAParticipantQuestions
        exclude = ["participant"]
        widgets = {
            'on_becoming_catholic': forms.RadioSelect(choices=m.BecomingCatholicChoices),
        }
