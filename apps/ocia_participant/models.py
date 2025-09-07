from django.db import models
from datetime import date
from django.core.exceptions import ValidationError
from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest
from typing import Type
from django.utils import timezone

'''
  __  __           _      _   _____         _      ____ _           _               
 |  \/  | ___   __| | ___| | |_   _|____  _| |_   / ___| |__   ___ (_) ___ ___  ___ 
 | |\/| |/ _ \ / _` |/ _ \ |   | |/ _ \ \/ / __| | |   | '_ \ / _ \| |/ __/ _ \/ __|
 | |  | | (_) | (_| |  __/ |   | |  __/>  <| |_  | |___| | | | (_) | | (_|  __/\__ \
 |_|  |_|\___/ \__,_|\___|_|   |_|\___/_/\_\\__|  \____|_| |_|\___/|_|\___\___||___/
                                                                                    
'''

class YesNoChoices(models.TextChoices):
    YES = "yes", "Yes"
    NO = "no", "No"

class UnknownChoices(models.TextChoices):
    YES = "yes", "Yes"
    NO = "no", "No"
    UNKNOWN = "unknown", "Not sure"

class SexChoices(models.TextChoices):
    MALE = "male", "Male"
    FEMALE = "female", "Female"

class MaritalStatusChoices(models.TextChoices):
    SINGLE = "single", "Single"
    MARRIED = "married", "Married"

class MarriageStatusChoices(models.TextChoices):
    MARRIED = "married", "Currently married"
    SEPARATED = "separated", "Separated"
    DIVORCED = "divorced", "Divorced"
    DECEASED = "deceased", "Spouse is deceased"

class DenominationChoices(models.TextChoices):
    CATHOLIC = "Catholic", "Catholic"
    ORTHODOX = "Orthodox", "Orthodox"
    BAPTIST = "Baptist", "Baptist"
    EPISCOPAL = "Episcopal/Anglican", "Episcopal/Anglican"
    LUTHERAN = "Lutheran", "Lutheran"
    REFORMED = "Reformed/Presbyterian", "Reformed/Presbyterian"
    METHODIST = "Methodist", "Methodist"
    PENTECOSTAL = "Pentecostal", "Pentecostal"
    NON_DENOM = "Non-denominational", "Non-denominational"
    OTHER = "other", "Other"

class ReligionChoices(models.TextChoices):
    CATHOLIC = "Catholic", "Christian (Catholic)"
    CHRISTIAN = "Christian", "Christian (Other)"
    JUDAISM = "Judaism", "Judaism"
    ISLAM = "Islam", "Islam"
    BUDDHISM = "Buddhism", "Buddhism"
    NONE = "none", "None"
    OTHER = "other", "Other"

class ParentTitleChoices(models.TextChoices):
    FATHER = "father", "Father"
    MOTHER = "mother", "Mother"

class BecomingCatholicChoices(models.TextChoices):
    UNLIKELY = "unlikely", "I am not really interested in becoming Catholic"
    UNDECIDED = "undecided", "I don't really know yet"
    POSSIBLE = "possible", "I am interested in possibly becoming Catholic"
    LIKELY = "likely", "I have every intention of becoming Catholic"

"""
  ___   ____ ___    _      ____            _   _      _                   _                         
 / _ \ / ___|_ _|  / \    |  _ \ __ _ _ __| |_(_) ___(_)_ __   __ _ _ __ | |_                       
| | | | |    | |  / _ \   | |_) / _` | '__| __| |/ __| | '_ \ / _` | '_ \| __|                      
| |_| | |___ | | / ___ \  |  __/ (_| | |  | |_| | (__| | |_) | (_| | | | | |_                       
 \___/ \____|___/_/   \_\ |_|   \__,_|_|   \__|_|\___|_| .__/ \__,_|_| |_|\__|                      
                                                       |_|                                          
 ____       _   _   _                                                                               
/ ___|  ___| |_| |_(_)_ __   __ _ ___                                                               
\___ \ / _ \ __| __| | '_ \ / _` / __|                                                              
 ___) |  __/ |_| |_| | | | | (_| \__ \                                                              
|____/ \___|\__|\__|_|_| |_|\__, |___/                                                              
                            |___/

"""

class OCIAParticipantSettings(models.Model):
    access_code = models.CharField(
        verbose_name='Access Code', 
        blank=False,
        null=False,
        help_text='Access code required for participants to be able to enter participant data.'
    )
    liturgical_year = models.CharField(
        verbose_name='Liturgical Year', 
        blank=False,
        null=False,
        help_text='OCIA class period (e.g. "2025-26").'
    )
    enable_editing = models.BooleanField(
        verbose_name='Enable Editing',
    )

    def clean(self):
        if OCIAParticipantSettings.objects.exclude(id=self.id).exists():
            raise ValidationError("Only one OCIAParticipantSettings instance is allowed.")

    def save(self, *args, **kwargs):
        self.full_clean()  # Enforce singleton validation
        super().save(*args, **kwargs)

    @classmethod
    def fetch(cls) -> 'OCIAParticipantSettings':
        obj = cls.objects.get(pk=1)
        return obj
        
    def __str__(self):
        return "OCIA Participant Settings"

    class Meta:
        verbose_name = "OCIA Participant Settings"
        verbose_name_plural = "OCIA Participant Settings"

'''
   ___   ____ ___    _      ____            _   _      _                   _   
  / _ \ / ___|_ _|  / \    |  _ \ __ _ _ __| |_(_) ___(_)_ __   __ _ _ __ | |_ 
 | | | | |    | |  / _ \   | |_) / _` | '__| __| |/ __| | '_ \ / _` | '_ \| __|
 | |_| | |___ | | / ___ \  |  __/ (_| | |  | |_| | (__| | |_) | (_| | | | | |_ 
  \___/ \____|___/_/   \_\ |_|   \__,_|_|   \__|_|\___|_| .__/ \__,_|_| |_|\__|
                                                        |_|                    
'''

class OCIAParticipant(models.Model):
    first_name = models.CharField(
        "First Name✽",
        max_length=1000,
        blank=True,
        default="",
        help_text="Legal first name."
    )
    last_name = models.CharField(
        "Last Name✽",
        max_length=1000,
        blank=True,
        default="",
        help_text="Legal last name."
    )
    suffix = models.CharField(
        "Suffix",
        max_length=100,
        blank=True,
        default="",
        help_text='Legal name suffix if necessary (e.g. "III", "Jr.", "Sr.", etc.).'
    )
    preferred_name = models.CharField(
        "Preferred Name",
        max_length=1000,
        blank=True,
        default="",
        help_text="If you have another first name that you would prefer to be called that is different than your legal first name, please enter it here. (NOTE: You can leave this field blank if your preferred name is the same as your first name listed above."
    )
    liturgical_year = models.CharField(
        verbose_name="Year",
        max_length=1000,
        blank=True,
        default="",
        help_text="OCIA liturgical year."
    )
    created_on = models.DateTimeField(
        verbose_name='Created On',
        help_text='OCIA participant record created on this data/time.',
        default=timezone.now
    )
    email = models.CharField(
        "Email✽",
        max_length=1000,
        blank=True,
        default="",
        help_text="Your email address."
    )
    phone = models.CharField(
        "Phone",
        max_length=20,
        blank=True,
        default="",
        help_text="Provide a good contact number (preferably one that can send and receive texts)."
    )
    can_text = models.CharField(
        "Can Text?",
        max_length=10,
        choices=YesNoChoices.choices,
        blank=True,
        default="",
        help_text="Can your phone and receive and send text messages?"
    )
    mailing_address = models.TextField(
        "Mailing Address",
        blank=True,
        default="",
        help_text="Full mailing address, city, state, zip code."
    )
    date_of_birth = models.DateField(
        "Date of Birth",
        null=True,
        blank=True,
        help_text="Date of your birth."
    )
    place_of_birth = models.CharField(
        "Place of Birth",
        max_length=1000,
        blank=True,
        default="",
        help_text="City, state (and country if other than the US) where you were born."
    )
    sex = models.CharField(
        "Sex",
        max_length=10,
        choices=SexChoices.choices,
        blank=True,
        default="",
        help_text="Biological sex."
    )
    marital_status = models.CharField(
        "Current Marital Status",
        max_length=10,
        choices=MaritalStatusChoices.choices,
        blank=True,
        default="",
        help_text="Are you currently single or married? NOTE: If you are separated from your spouse but have not gotten a divorce, please answer \"Married\"."
    )
    num_marriages = models.CharField(
        "Number of Marriages✽",
        max_length=10,
        blank=True,
        default="",
        help_text="Indicate the total number of times you have been married. Please include your current marriage in this count (if you are married now)."
    )
    engaged = models.CharField(
        "Engaged?✽",
        max_length=10,
        choices=YesNoChoices.choices,
        blank=True,
        default="",
        help_text="If not married, are you are engaged to be married?"
    )

    @property
    def age(self) -> int | None:
        if not isinstance(self.date_of_birth, date):
            return None
        today = date.today()
        age = today.year - self.date_of_birth.year
        if (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day):
            age -= 1
        return age
    
    @property
    def full_name(self) -> str:
        preferred_name = str(self.preferred_name).strip()
        first_name = str(self.first_name).strip()
        last_name = str(self.last_name).strip()
        suffix = str(self.suffix).strip()
        name = first_name
        if preferred_name: name = preferred_name
        if last_name: name += ' ' + last_name
        if suffix: name += ' ' + suffix
        return name

    class Meta:
        verbose_name = "OCIA Participant"
        verbose_name_plural = "OCIA Participants"
    def __str__(self):
        return f"{self.full_name}".strip() or "Unnamed Participant"

'''
   ___   ____ ___    _      ____            _   _      _                   _   
  / _ \ / ___|_ _|  / \    |  _ \ __ _ _ __| |_(_) ___(_)_ __   __ _ _ __ | |_ 
 | | | | |    | |  / _ \   | |_) / _` | '__| __| |/ __| | '_ \ / _` | '_ \| __|
 | |_| | |___ | | / ___ \  |  __/ (_| | |  | |_| | (__| | |_) | (_| | | | | |_ 
  \___/ \____|___/_/   \_\ |_|   \__,_|_|   \__|_|\___|_| .__/ \__,_|_| |_|\__|
  ____      _ _       _                                 |_|                    
 |  _ \ ___| (_) __ _(_) ___  _ __                                             
 | |_) / _ \ | |/ _` | |/ _ \| '_ \                                            
 |  _ <  __/ | | (_| | | (_) | | | |                                           
 |_| \_\___|_|_|\__, |_|\___/|_| |_|                                           
                |___/                                                          
'''

class OCIAParticipantReligion(models.Model):
    participant = models.OneToOneField(
        "OCIAParticipant",
        on_delete=models.CASCADE,
        related_name="religion",
        null=True,
        blank=True
    )
    affiliation = models.CharField(
        "Religion Affiliation",
        max_length=100,
        blank=True,
        default="",
        choices=ReligionChoices.choices,
        help_text="Are you affiliated with any religious faith?"
    )
    affiliation_other = models.CharField(
        "Religion Affiliation Other",
        max_length=100,
        blank=True,
        default="",
        help_text="If religious affiliation is \"other\" please specify that faith here."
    )
    baptized = models.CharField(
        "Are You Baptized?",
        max_length=10,
        choices=UnknownChoices.choices,
        blank=True,
        default="",
        help_text="Have you ever been baptized into any Christian faith?"
    )
    baptized_denomination = models.CharField(
        "Baptism Denomination",
        max_length=50,
        choices=DenominationChoices.choices,
        blank=True,
        default="",
        help_text="Into which Christian faith where you baptized?"
    )
    baptized_denomination_other = models.CharField(
        "Baptism Denomination Other",
        max_length=100,
        blank=True,
        default="",
        help_text="If baptized in some other denomination, indicate which one here."
    )
    baptized_on = models.DateField(
        "Date of Baptism",
        null=True,
        blank=True,
        help_text="When were you baptized?"
    )
    baptism_info = models.TextField(
        "Baptism Details",
        blank=True,
        default="",
        help_text="Name and location of church where you were baptized. (Please provide as much detail as possible.)"
    )
    sacrament_of_confession = models.CharField(
        "Sacrament of Confession?",
        max_length=10,
        choices=UnknownChoices.choices,
        blank=True,
        default="",
        help_text="If you were baptized Catholic, did you ever receive the Sacrament of Reconciliation (otherwise known as Confession)?"
    )
    sacrament_of_communion = models.CharField(
        "Sacrament of Communion?",
        max_length=10,
        choices=UnknownChoices.choices,
        blank=True,
        default="",
        help_text="If you were baptized Catholic, did you ever receive Holy Communion (otherwise known as the Sacrament of the Eucharist)?"
    )
    sacrament_of_confirmation = models.CharField(
        "Sacrament of Confirmation?",
        max_length=10,
        choices=UnknownChoices.choices,
        blank=True,
        default="",
        help_text="If you were baptized Catholic, did you ever receive the Sacrament of Confirmation?"
    )
    admin_notes = models.TextField(
        "Admin Notes",
        blank=True,
        default="",
        help_text="Record any private / admin notes."
    )

'''
   ___   ____ ___    _      ____            _   _      _                   _   
  / _ \ / ___|_ _|  / \    |  _ \ __ _ _ __| |_(_) ___(_)_ __   __ _ _ __ | |_ 
 | | | | |    | |  / _ \   | |_) / _` | '__| __| |/ __| | '_ \ / _` | '_ \| __|
 | |_| | |___ | | / ___ \  |  __/ (_| | |  | |_| | (__| | |_) | (_| | | | | |_ 
  \___/ \____|___/_/   \_\ |_|   \__,_|_|   \__|_|\___|_| .__/ \__,_|_| |_|\__|
  __  __                 _                              |_|                    
 |  \/  | __ _ _ __ _ __(_) __ _  __ _  ___                                    
 | |\/| |/ _` | '__| '__| |/ _` |/ _` |/ _ \                                   
 | |  | | (_| | |  | |  | | (_| | (_| |  __/                                   
 |_|  |_|\__,_|_|  |_|  |_|\__,_|\__, |\___|                                   
                                 |___/                                         
'''

class OCIAParticipantMarriage(models.Model):
    participant = models.ForeignKey(
        "OCIAParticipant",
        on_delete=models.CASCADE,
        related_name="marriages"
    )
    spouse_name = models.CharField(
        "Spouse's Full Name",
        max_length=1000,
        blank=True,
        default="",
        help_text="Your spouse's full name."
    )
    status = models.CharField(
        "Marriage Status",
        max_length=10,
        choices=MarriageStatusChoices.choices,
        blank=True,
        default="",
        help_text="Current state of the marriage."
    )
    date_of_marriage = models.DateField(
        "Date of Marriage",
        null=True,
        blank=True,
        help_text="Date you were married."
    )
    date_of_divorce = models.DateField(
        "Date of Divorce",
        null=True,
        blank=True,
        help_text="If divorced, record the date of the legally finalized divorce."
    )
    spouse_first_marriage = models.CharField(
        "Spouse's First Marriage?",
        max_length=10,
        choices=YesNoChoices.choices,
        blank=True,
        default="",
        help_text="Was this your spouse's first marriage at the time?"
    )
    spouse_religion = models.CharField(
        "Spouse's Religious Affiliation",
        max_length=1000,
        blank=True,
        default="",
        help_text="What is/was your spouse's religious affiliation?"
    )
    notes = models.TextField(
        "Marriage Details",
        blank=True,
        default="",
        help_text="Where was the service held? Was it a Catholic or Christian service? Who was the minister (e.g. priest, pastor, deacon, Justice of the Peace, etc.)? Record any additional notes you may think are significant."
    )
    admin_notes = models.TextField(
        "Admin Notes",
        blank=True,
        default="",
        help_text="Record any private / admin notes."
    )
    class Meta:
        verbose_name = "OCIA Participant Marriage"
        verbose_name_plural = "OCIA Participant Marriages"
    def __str__(self):
        name = str(self.spouse_name).strip()
        if not name: return 'Marriage info not recorded'
        status = str(self.status).strip()
        if status: name += f' ({status})'
        return f'Marriage to {name}'

'''
   ___   ____ ___    _      ____            _   _      _                   _   
  / _ \ / ___|_ _|  / \    |  _ \ __ _ _ __| |_(_) ___(_)_ __   __ _ _ __ | |_ 
 | | | | |    | |  / _ \   | |_) / _` | '__| __| |/ __| | '_ \ / _` | '_ \| __|
 | |_| | |___ | | / ___ \  |  __/ (_| | |  | |_| | (__| | |_) | (_| | | | | |_ 
  \___/ \____|___/_/   \_\ |_|   \__,_|_|   \__|_|\___|_| .__/ \__,_|_| |_|\__|
                                                        |_|                    
  _____                                                   _                    
 | ____|_ __   __ _  __ _  __ _  ___ _ __ ___   ___ _ __ | |_                  
 |  _| | '_ \ / _` |/ _` |/ _` |/ _ \ '_ ` _ \ / _ \ '_ \| __|                 
 | |___| | | | (_| | (_| | (_| |  __/ | | | | |  __/ | | | |_                  
 |_____|_| |_|\__, |\__,_|\__, |\___|_| |_| |_|\___|_| |_|\__|                 
              |___/       |___/                                                
'''
    
class OCIAParticipantEngagement(models.Model):
    participant = models.OneToOneField(
        "OCIAParticipant",
        on_delete=models.CASCADE,
        related_name="engagement",
        null=True,
        blank=True
    )

    fiance_name = models.CharField(
        "Fiance's Full Name",
        max_length=1000,
        blank=True,
        default="",
        help_text="Your fiance's full name."
    )

    planned_date_of_marriage = models.DateField(
        "Planned Date of Marriage",
        null=True,
        blank=True,
        help_text="Date you are planning to get married (if known)."
    )

    fiance_religion = models.CharField(
        "Fiance's Religious Affiliation",
        max_length=1000,
        blank=True,
        default="",
        help_text="What is your fiance's religious affiliation?"
    )

    your_first_marriage = models.CharField(
        "Your First Marriage?",
        max_length=10,
        choices=YesNoChoices.choices,
        blank=True,
        default="",
        help_text="Will this be your first marriage?"
    )

    fiance_first_marriage = models.CharField(
        "Fiance's First Marriage?",
        max_length=10,
        choices=YesNoChoices.choices,
        blank=True,
        default="",
        help_text="Will this be your fiance's first marriage?"
    )

    notes = models.TextField(
        "Marriage Details",
        blank=True,
        default="",
        help_text="Record any additional notes you think may be important."
    )

    admin_notes = models.TextField(
        "Admin Notes",
        blank=True,
        default="",
        help_text="Record any private / admin notes."
    )

    class Meta:
        verbose_name = "OCIA Participant Engagement"
        verbose_name_plural = "OCIA Participant Engagement"
    def __str__(self):
        return f"Engagement to {self.fiance_name}".strip() or f"No Engagement Info"


'''
   ___   ____ ___    _      ____            _   _      _                   _   
  / _ \ / ___|_ _|  / \    |  _ \ __ _ _ __| |_(_) ___(_)_ __   __ _ _ __ | |_ 
 | | | | |    | |  / _ \   | |_) / _` | '__| __| |/ __| | '_ \ / _` | '_ \| __|
 | |_| | |___ | | / ___ \  |  __/ (_| | |  | |_| | (__| | |_) | (_| | | | | |_ 
  \___/ \____|___/_/   \_\ |_|   \__,_|_|   \__|_|\___|_| .__/ \__,_|_| |_|\__|
  ____                      _                           |_|                    
 |  _ \ __ _ _ __ ___ _ __ | |_                                                
 | |_) / _` | '__/ _ \ '_ \| __|                                               
 |  __/ (_| | | |  __/ | | | |_                                                
 |_|   \__,_|_|  \___|_| |_|\__|                                               
                                                                               
'''

class OCIAParticipantParent(models.Model):
    participant = models.ForeignKey(
        OCIAParticipant, 
        on_delete=models.CASCADE, 
        related_name="parents"
    )
    name = models.CharField(
        "Parent's Full Name",
        blank=True,
        default="",
        max_length=100, 
        help_text="Full name of the parent."
    )
    relationship = models.CharField(
        "Parent Relationship",
        blank=True,
        default="",
        max_length=100, 
        choices=ParentTitleChoices.choices,
        help_text="Relationship to participant (e.g., mother, father)."
    )
    religion = models.CharField(
        "Parent's Religious Affiliation",
        blank=True,
        default="",
        max_length=100, 
        help_text="Religious affiliation, if known."
    )
    class Meta:
        verbose_name = "OCIA Participant (Parent Info)"
        verbose_name_plural = "OCIA Participant (Parent Info)"
    def __str__(self):
        name = str(self.name).strip()
        if name == '': return "No name specified" 
        relationship = str(self.relationship).strip()
        if relationship: name += f' ({relationship})'
        return name

'''
   ___   ____ ___    _      ____            _   _      _                   _   
  / _ \ / ___|_ _|  / \    |  _ \ __ _ _ __| |_(_) ___(_)_ __   __ _ _ __ | |_ 
 | | | | |    | |  / _ \   | |_) / _` | '__| __| |/ __| | '_ \ / _` | '_ \| __|
 | |_| | |___ | | / ___ \  |  __/ (_| | |  | |_| | (__| | |_) | (_| | | | | |_ 
  \___/ \____|___/_/   \_\ |_|   \__,_|_|   \__|_|\___|_| .__/ \__,_|_| |_|\__|
   ___                  _   _                           |_|                    
  / _ \ _   _  ___  ___| |_(_) ___  _ __  ___                                  
 | | | | | | |/ _ \/ __| __| |/ _ \| '_ \/ __|                                 
 | |_| | |_| |  __/\__ \ |_| | (_) | | | \__ \                                 
  \__\_\\__,_|\___||___/\__|_|\___/|_| |_|___/                                 
                                                                               
'''

class OCIAParticipantQuestions(models.Model):
    participant = models.OneToOneField(
        "OCIAParticipant",
        on_delete=models.CASCADE,
        related_name="questions",
        null=True,
        blank=True
    )

    reason_for_attending_class = models.TextField(
        "Reason for Attending OCIA?",
        blank=True,
        default="",
        help_text="What or who has led you to want to know more about the Catholic faith?"
    )

    religious_education = models.TextField(
        "Religious Education?",
        blank=True,
        default="",
        help_text="Describe any religious education you have received, either as a child or as an adult."
    )

    questions_or_concerns = models.TextField(
        "Questions or Concerns?",
        blank=True,
        default="",
        help_text="Do you have any questions or concerns about the Catholic Church that you would like to have addressed publicly in class, or discretely in a private meeting?"
    )

    on_becoming_catholic = models.CharField(
        "On the Possibility of Becoming Catholic?",
        max_length=100,
        blank=True,
        default="",
        choices=BecomingCatholicChoices.choices,
        help_text='How likely are you to become Catholic?'
    )

    on_becoming_catholic_comments = models.TextField(
        "Can You Expound?",
        blank=True,
        default="",
        help_text="Can you expound on the the answer you gave in the previous question?"
    )
    class Meta:
        verbose_name = "OCIA Participant (Questions)"
        verbose_name_plural = "OCIA Participant (Questions)"
    def __str__(self):
        return f"{self.participant} Q&A" or "Q&A"
