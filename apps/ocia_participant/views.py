from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpRequest
from main.models import SiteSettings
import ocia_participant.models as m
import ocia_participant.forms as f
import hashlib
import ru, cronos
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic import TemplateView
import secrets
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.views.decorators.http import require_http_methods, require_GET
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.urls import reverse
import re
from django.core.management import call_command
from django.conf import settings
from django.core.mail import EmailMultiAlternatives


"""
      _                                   _              _                                          
  ___| | ___  __ _ _ __    _____  ___ __ (_)_ __ ___  __| |                                         
 / __| |/ _ \/ _` | '__|  / _ \ \/ / '_ \| | '__/ _ \/ _` |                                         
| (__| |  __/ (_| | |    |  __/>  <| |_) | | | |  __/ (_| |                                         
 \___|_|\___|\__,_|_|     \___/_/\_\ .__/|_|_|  \___|\__,_|                                         
                                   |_|                                                              
                   _                                                                                
 ___  ___  ___ ___(_) ___  _ __  ___                                                                
/ __|/ _ \/ __/ __| |/ _ \| '_ \/ __|                                                               
\__ \  __/\__ \__ \ | (_) | | | \__ \                                                               
|___/\___||___/___/_|\___/|_| |_|___/

"""

def clear_expired_sessions():
    call_command('clearsessions')

"""
  ___   ____ ___    _      ____            _   _      _                   _                         
 / _ \ / ___|_ _|  / \    |  _ \ __ _ _ __| |_(_) ___(_)_ __   __ _ _ __ | |_                       
| | | | |    | |  / _ \   | |_) / _` | '__| __| |/ __| | '_ \ / _` | '_ \| __|                      
| |_| | |___ | | / ___ \  |  __/ (_| | |  | |_| | (__| | |_) | (_| | | | | |_                       
 \___/ \____|___/_/   \_\ |_|   \__,_|_|   \__|_|\___|_| .__/ \__,_|_| |_|\__|                      
                                                       |_|                                          
__     ___                                                                                          
\ \   / (_) _____      __                                                                           
 \ \ / /| |/ _ \ \ /\ / /                                                                           
  \ V / | |  __/\ V  V /                                                                            
   \_/  |_|\___| \_/\_/

"""

class OCIAParticipantView:
    session_keys = ('participant_id', 'participant_id_temp', 'participant_access_code', 
                    'participant_debug_mode', 'participant_error_message', 'participant_create_enabled',
                    'participant_email')

    def __init__(self, request:HttpRequest) -> None:
        self.request = request
        self.site_settings = SiteSettings.fetch()
        self.app_settings = m.OCIAParticipantSettings.fetch()
        self.enable_editing = self.app_settings.enable_editing
        self.participant_id = self.request.session.get("participant_id")
        self.participant = None
        if self.participant_id:
            try:
                self.participant = m.OCIAParticipant.objects.get(id=self.participant_id)
            except Exception as err:
                self.participant = None

    def clear_session(self) -> None:
        for key in self.session_keys:
            if key in self.request.session:
                del self.request.session[key]

    def error(self, message) -> HttpResponse:
        self.request.session["participant_error_message"] = message
        return redirect("OCIAParticipantErrorView")

    def not_logged_in_error(self) -> HttpResponse:
        self.request.session["participant_error_message"] = f'''It does not appear that you are logged in. Click <a href="{reverse('OCIAParticipantLoginView')}">login</a> to go to the login page and follow the specified steps.'''
        return redirect("OCIAParticipantErrorView")

    def editing_disabled_error(self) -> HttpResponse:
        self.request.session["participant_error_message"] = f'''Editing OCIA participant data is currently disabled.'''
        return redirect("OCIAParticipantErrorView")

"""
  ___   ____ ___    _      ____            _   _      _                   _                         
 / _ \ / ___|_ _|  / \    |  _ \ __ _ _ __| |_(_) ___(_)_ __   __ _ _ __ | |_                       
| | | | |    | |  / _ \   | |_) / _` | '__| __| |/ __| | '_ \ / _` | '_ \| __|                      
| |_| | |___ | | / ___ \  |  __/ (_| | |  | |_| | (__| | |_) | (_| | | | | |_                       
 \___/ \____|___/_/   \_\ |_|   \__,_|_|   \__|_|\___|_| .__/ \__,_|_| |_|\__|                      
                                                       |_|                                          
 _____         _    __     ___                                                                      
|_   _|__  ___| |_  \ \   / (_) _____      __                                                       
  | |/ _ \/ __| __|  \ \ / /| |/ _ \ \ /\ / /                                                       
  | |  __/\__ \ |_    \ V / | |  __/\ V  V /                                                        
  |_|\___||___/\__|    \_/  |_|\___| \_/\_/

"""

@require_http_methods(["GET", "POST"])
def OCIAParticipantTestView(request:HttpRequest) -> HttpResponse:
    context = {
        "site": SiteSettings.fetch()
    }
    # print(settings.EMAIL_HOST_USER)
    # print(settings.EMAIL_HOST_PASSWORD)
    return render(request, "ocia/ocia-participant-test-page.html", context)

"""
  ___   ____ ___    _      ____            _   _      _                   _                         
 / _ \ / ___|_ _|  / \    |  _ \ __ _ _ __| |_(_) ___(_)_ __   __ _ _ __ | |_                       
| | | | |    | |  / _ \   | |_) / _` | '__| __| |/ __| | '_ \ / _` | '_ \| __|                      
| |_| | |___ | | / ___ \  |  __/ (_| | |  | |_| | (__| | |_) | (_| | | | | |_                       
 \___/ \____|___/_/   \_\ |_|   \__,_|_|   \__|_|\___|_| .__/ \__,_|_| |_|\__|                      
                                                       |_|                                          
 _                            _    __     ___                                                       
| |    ___   __ _  ___  _   _| |_  \ \   / (_) _____      __                                        
| |   / _ \ / _` |/ _ \| | | | __|  \ \ / /| |/ _ \ \ /\ / /                                        
| |__| (_) | (_| | (_) | |_| | |_    \ V / | |  __/\ V  V /                                         
|_____\___/ \__, |\___/ \__,_|\__|    \_/  |_|\___| \_/\_/                                          
            |___/

"""

@require_http_methods(["GET", "POST"])
def OCIAParticipantLogoutView(request:HttpRequest) -> HttpResponse:
    view = OCIAParticipantView(request)
    participant_id = request.session.pop("participant_id", None)
    if participant_id is None:
        return view.error('Not logged in. Do you want to <a href="' + reverse("OCIAParticipantLoginView") + '">login</a>?')
    view.clear_session()
    context = {
        "site": view.site_settings,
    }
    return render(request, "ocia/ocia-participant-logout-page.html", context)

"""
  ___   ____ ___    _      ____            _   _      _                   _                         
 / _ \ / ___|_ _|  / \    |  _ \ __ _ _ __| |_(_) ___(_)_ __   __ _ _ __ | |_                       
| | | | |    | |  / _ \   | |_) / _` | '__| __| |/ __| | '_ \ / _` | '_ \| __|                      
| |_| | |___ | | / ___ \  |  __/ (_| | |  | |_| | (__| | |_) | (_| | | | | |_                       
 \___/ \____|___/_/   \_\ |_|   \__,_|_|   \__|_|\___|_| .__/ \__,_|_| |_|\__|                      
                                                       |_|                                          
 _                _        __     ___                                                               
| |    ___   __ _(_)_ __   \ \   / (_) _____      __                                                
| |   / _ \ / _` | | '_ \   \ \ / /| |/ _ \ \ /\ / /                                                
| |__| (_) | (_| | | | | |   \ V / | |  __/\ V  V /                                                 
|_____\___/ \__, |_|_| |_|    \_/  |_|\___| \_/\_/                                                  
            |___/

"""

@require_http_methods(["GET"])
def OCIAParticipantStartView(request:HttpRequest) -> HttpResponse:
    return redirect('OCIAParticipantLoginView')

@require_http_methods(["GET", "POST"])
def OCIAParticipantLoginView(request:HttpRequest) -> HttpResponse:
    # $$$ Clear expired sessions.
    clear_expired_sessions()
    # $$$ If already logged in, redirect to the OCIA Participant Navigation page.
    view = OCIAParticipantView(request)
    if view.participant:
        return redirect('OCIAParticipantNavigationView')
    # $$$ If not already logged in, request the user's email address.
    form = f.OCIAParticipantLoginForm(request.POST or None)
    error = None
    if request.method == "POST" and form.is_valid():
        try:
            email = str(form.cleaned_data["email"]).strip().lower()
            validate_email(email)
        except Exception as err:
            return view.error(f'Invalid email address entered: "{email}". {err}')
        try:
            participant = m.OCIAParticipant.objects.filter(email__iexact=email).first()
            if participant is None:
                request.session["participant_create_enabled"] = -1
                request.session["participant_access_code"] = hashlib.sha256(secrets.token_bytes(32)).hexdigest()[0:32]
                request.session["participant_debug_mode"] = True if email.endswith('@fake.com') else False
                request.session["participant_email"] = email
                return redirect('OCIAParticipantEmailAccessNewView')
            else:
                request.session["participant_id_temp"] = participant.id
                request.session["participant_access_code"] = hashlib.sha256(secrets.token_bytes(32)).hexdigest()[0:32]
                request.session["participant_debug_mode"] = True if email.endswith('@fake.com') else False
                request.session["participant_email"] = email
                return redirect('OCIAParticipantEmailAccessExistingView')
        except Exception as err:
            return view.error(f'Invalid request.')
    context = {
        "form": form,
        "site": SiteSettings.fetch(),
        "error": error,
    }
    return render(request, "ocia/ocia-participant-login-page.html", context)

"""
            _ _     _       _                              _ _                                      
__   ____ _| (_) __| | __ _| |_ ___    ___ _ __ ___   __ _(_) |                                     
\ \ / / _` | | |/ _` |/ _` | __/ _ \  / _ \ '_ ` _ \ / _` | | |                                     
 \ V / (_| | | | (_| | (_| | ||  __/ |  __/ | | | | | (_| | | |                                     
  \_/ \__,_|_|_|\__,_|\__,_|\__\___|  \___|_| |_| |_|\__,_|_|_|

"""

def validate_email(value) -> bool:
    if not isinstance(value, str):
        raise ValueError("Email must be a string.")
    value = value.strip()
    if not value:
        raise ValueError("Email cannot be empty.")
    # Basic structure check
    if '@' not in value:
        raise ValueError("Email must contain '@' separating local and domain parts.")
    local, sep, domain = value.partition('@')
    if not local:
        raise ValueError("Email must have characters before '@'.")
    if not domain:
        raise ValueError("Email must have a domain after '@'.")
    # Check for invalid characters in local part
    if not re.match(r"^[A-Za-z0-9._%+-]+$", local):
        raise ValueError("Local part contains invalid characters. Only letters, digits, '.', '_', '%', '+', and '-' are allowed.")
    # Domain must contain at least one dot
    if '.' not in domain:
        raise ValueError("Domain must contain at least one '.' (e.g., 'example.com').")
    # Check for valid domain structure
    if not re.match(r"^[A-Za-z0-9.-]+\.[A-Za-z]{2,}$", domain):
        raise ValueError("Domain format is invalid. It should end with a valid top-level domain (e.g., '.com', '.org').")
    # No consecutive dots
    if '..' in value:
        raise ValueError("Email cannot contain consecutive dots.")
    # No leading or trailing dots in local or domain
    if local.startswith('.') or local.endswith('.'):
        raise ValueError("Local part cannot start or end with a dot.")
    if domain.startswith('.') or domain.endswith('.'):
        raise ValueError("Domain cannot start or end with a dot.")
    return True

"""
  ___   ____ ___    _      ____            _   _      _                   _                         
 / _ \ / ___|_ _|  / \    |  _ \ __ _ _ __| |_(_) ___(_)_ __   __ _ _ __ | |_                       
| | | | |    | |  / _ \   | |_) / _` | '__| __| |/ __| | '_ \ / _` | '_ \| __|                      
| |_| | |___ | | / ___ \  |  __/ (_| | |  | |_| | (__| | |_) | (_| | | | | |_                       
 \___/ \____|___/_/   \_\ |_|   \__,_|_|   \__|_|\___|_| .__/ \__,_|_| |_|\__|                      
                                                       |_|                                          
 _____                 _ _      _                                                                   
| ____|_ __ ___   __ _(_) |    / \   ___ ___ ___  ___ ___                                           
|  _| | '_ ` _ \ / _` | | |   / _ \ / __/ __/ _ \/ __/ __|                                          
| |___| | | | | | (_| | | |  / ___ \ (_| (_|  __/\__ \__ \                                          
|_____|_| |_| |_|\__,_|_|_| /_/   \_\___\___\___||___/___/                                          
                                                                                                    
__     ___                                                                                          
\ \   / (_) _____      __                                                                           
 \ \ / /| |/ _ \ \ /\ / /                                                                           
  \ V / | |  __/\ V  V /                                                                            
   \_/  |_|\___| \_/\_/

"""

@require_http_methods(["GET"])
def OCIAParticipantEmailAccessExistingView(request:HttpRequest) -> HttpResponse:
    view = OCIAParticipantView(request)
    access_code = request.session.get("participant_access_code", None)
    if access_code is None:
        return view.error('Invalid request.')
    url = request.scheme + "://" + request.get_host() + reverse('OCIAParticipantAccessConfirmationExistingView', kwargs={"code": access_code})
    
    user_email = request.session.pop("participant_email")

    text_content = []
    text_content.append(f'Hello!')
    text_content.append(f'Are you attempting to login to the Sacred Heart Catholic Church - OCIA Participant form? If so copy-paste the link below into your web browser:')
    text_content.append(f'{url}')
    text_content.append(f'If this request did not originate from you, please ignore this message.')
    text_content.append(f'Regards,')
    text_content.append(f'Sacred Heart Catholic Church')
    text_content.append(f'NOTE: This message was sent from an unmonitored address. If you have questions or need assistance, please contact us through our website or parish office.')
    text_content = '\n\n'.join(text_content)

    html_content = []
    html_content.append(f'Hello!')
    html_content.append(f'Are you attempting to login to the <strong>Sacred Heart Catholic Church - OCIA Participant</strong> form? If so, click the link below, or copy-paste it into your web browser:')
    html_content.append(f'<a href="{url}">{url}</a>')
    html_content.append(f'If this request did not originate from you, please ignore this message.')
    html_content.append(f'Regards,')
    html_content.append(f'<strong>Sacred Heart Catholic Church</strong>')
    html_content.append(f'<strong>NOTE</strong>: This message was sent from an unmonitored address. If you have questions or need assistance, please contact us through our website or parish office.')
    html_content = ''.join(f'<p>{line}</p>' for line in html_content)

    try:
        email = EmailMultiAlternatives('Sacred Heart - OCIA Participant Login', text_content, settings.EMAIL_HOST_USER, [user_email])
        email.attach_alternative(html_content, "text/html")
        email.send()
    except Exception as err:
        request.session["participant_error_message"] = f'Our system tried to send a login email with your access code to {user_email} but failed: {err}'
        return redirect('OCIAParticipantErrorView')

    context = {
        "site": SiteSettings.fetch(),
        "url": url,
        "fake": request.session.get("participant_debug_mode", False),
    }
    request.session.pop("participant_debug_mode", None)
    return render(request, "ocia/ocia-participant-email-access-existing-page.html", context)

"""
  ___   ____ ___    _      ____            _   _      _                   _                         
 / _ \ / ___|_ _|  / \    |  _ \ __ _ _ __| |_(_) ___(_)_ __   __ _ _ __ | |_                       
| | | | |    | |  / _ \   | |_) / _` | '__| __| |/ __| | '_ \ / _` | '_ \| __|                      
| |_| | |___ | | / ___ \  |  __/ (_| | |  | |_| | (__| | |_) | (_| | | | | |_                       
 \___/ \____|___/_/   \_\ |_|   \__,_|_|   \__|_|\___|_| .__/ \__,_|_| |_|\__|                      
                                                       |_|                                          
 _____                 _ _      _                                                                   
| ____|_ __ ___   __ _(_) |    / \   ___ ___ ___  ___ ___                                           
|  _| | '_ ` _ \ / _` | | |   / _ \ / __/ __/ _ \/ __/ __|                                          
| |___| | | | | | (_| | | |  / ___ \ (_| (_|  __/\__ \__ \                                          
|_____|_| |_| |_|\__,_|_|_| /_/   \_\___\___\___||___/___/                                          
                                                                                                    
 _   _                __     ___                                                                    
| \ | | _____      __ \ \   / (_) _____      __                                                     
|  \| |/ _ \ \ /\ / /  \ \ / /| |/ _ \ \ /\ / /                                                     
| |\  |  __/\ V  V /    \ V / | |  __/\ V  V /                                                      
|_| \_|\___| \_/\_/      \_/  |_|\___| \_/\_/

"""

@require_http_methods(["GET"])
def OCIAParticipantEmailAccessNewView(request:HttpRequest) -> HttpResponse:
    view = OCIAParticipantView(request)
    access_code = request.session.get("participant_access_code", None)
    if access_code is None:
        return view.error('Invalid request.')
    url = request.scheme + "://" + request.get_host() + reverse('OCIAParticipantAccessConfirmationNewView', kwargs={"code": access_code})
    
    user_email = request.session.pop("participant_email")

    text_content = []
    text_content.append(f'Hello!')
    text_content.append(f'Are you attempting to login to the Sacred Heart Catholic Church - OCIA Participant form? If so copy-paste the link below into your web browser:')
    text_content.append(f'{url}')
    text_content.append(f'If this request did not originate from you, please ignore this message.')
    text_content.append(f'Regards,')
    text_content.append(f'Sacred Heart Catholic Church')
    text_content.append(f'NOTE: This message was sent from an unmonitored address. If you have questions or need assistance, please contact us through our website or parish office.')
    text_content = '\n\n'.join(text_content)

    html_content = []
    html_content.append(f'Hello!')
    html_content.append(f'Are you attempting to login to the <strong>Sacred Heart Catholic Church - OCIA Participant</strong> form? If so, click the link below, or copy-paste it into your web browser:')
    html_content.append(f'<a href="{url}">{url}</a>')
    html_content.append(f'If this request did not originate from you, please ignore this message.')
    html_content.append(f'Regards,')
    html_content.append(f'<strong>Sacred Heart Catholic Church</strong>')
    html_content.append(f'<strong>NOTE</strong>: This message was sent from an unmonitored address. If you have questions or need assistance, please contact us through our website or parish office.')
    html_content = ''.join(f'<p>{line}</p>' for line in html_content)

    try:
        email = EmailMultiAlternatives('Sacred Heart - OCIA Participant Login', text_content, settings.EMAIL_HOST_USER, [user_email])
        email.attach_alternative(html_content, "text/html")
        email.send()
    except Exception as err:
        request.session["participant_error_message"] = f'Our system tried to send a login email with your access code to {user_email} but failed: {err}'
        return redirect('OCIAParticipantErrorView')

    context = {
        "site": SiteSettings.fetch(),
        "url": url,
        "fake": request.session.get("participant_debug_mode", False),
    }
    return render(request, "ocia/ocia-participant-email-access-new-page.html", context)

"""
  ___   ____ ___    _      ____            _   _      _                   _                         
 / _ \ / ___|_ _|  / \    |  _ \ __ _ _ __| |_(_) ___(_)_ __   __ _ _ __ | |_                       
| | | | |    | |  / _ \   | |_) / _` | '__| __| |/ __| | '_ \ / _` | '_ \| __|                      
| |_| | |___ | | / ___ \  |  __/ (_| | |  | |_| | (__| | |_) | (_| | | | | |_                       
 \___/ \____|___/_/   \_\ |_|   \__,_|_|   \__|_|\___|_| .__/ \__,_|_| |_|\__|                      
                                                       |_|                                          
    _                                                                                               
   / \   ___ ___ ___  ___ ___                                                                       
  / _ \ / __/ __/ _ \/ __/ __|                                                                      
 / ___ \ (_| (_|  __/\__ \__ \                                                                      
/_/   \_\___\___\___||___/___/                                                                      
                                                                                                    
  ____             __ _                      _   _                                                  
 / ___|___  _ __  / _(_)_ __ _ __ ___   __ _| |_(_) ___  _ __                                       
| |   / _ \| '_ \| |_| | '__| '_ ` _ \ / _` | __| |/ _ \| '_ \                                      
| |__| (_) | | | |  _| | |  | | | | | | (_| | |_| | (_) | | | |                                     
 \____\___/|_| |_|_| |_|_|  |_| |_| |_|\__,_|\__|_|\___/|_| |_|                                     
                                                                                                    
__     ___                                                                                          
\ \   / (_) _____      __                                                                           
 \ \ / /| |/ _ \ \ /\ / /                                                                           
  \ V / | |  __/\ V  V /                                                                            
   \_/  |_|\___| \_/\_/

"""

@require_http_methods(["GET"])
def OCIAParticipantAccessConfirmationExistingView(request:HttpRequest, code:str) -> HttpResponse:
    url_code = code
    saved_code = request.session.get("participant_access_code", '')
    request.session.pop("participant_access_code", None)
    if saved_code == url_code:
        request.session["participant_id"] = request.session["participant_id_temp"]
        request.session.pop("participant_id_temp", None)
        return redirect('OCIAParticipantNavigationView')
    else:
        request.session["participant_error_message"] = "Access denied."
        return redirect('OCIAParticipantErrorView')

"""
  ___   ____ ___    _      ____            _   _      _                   _                         
 / _ \ / ___|_ _|  / \    |  _ \ __ _ _ __| |_(_) ___(_)_ __   __ _ _ __ | |_                       
| | | | |    | |  / _ \   | |_) / _` | '__| __| |/ __| | '_ \ / _` | '_ \| __|                      
| |_| | |___ | | / ___ \  |  __/ (_| | |  | |_| | (__| | |_) | (_| | | | | |_                       
 \___/ \____|___/_/   \_\ |_|   \__,_|_|   \__|_|\___|_| .__/ \__,_|_| |_|\__|                      
                                                       |_|                                          
    _                                                                                               
   / \   ___ ___ ___  ___ ___                                                                       
  / _ \ / __/ __/ _ \/ __/ __|                                                                      
 / ___ \ (_| (_|  __/\__ \__ \                                                                      
/_/   \_\___\___\___||___/___/                                                                      
                                                                                                    
  ____             __ _                      _   _                                                  
 / ___|___  _ __  / _(_)_ __ _ __ ___   __ _| |_(_) ___  _ __                                       
| |   / _ \| '_ \| |_| | '__| '_ ` _ \ / _` | __| |/ _ \| '_ \                                      
| |__| (_) | | | |  _| | |  | | | | | | (_| | |_| | (_) | | | |                                     
 \____\___/|_| |_|_| |_|_|  |_| |_| |_|\__,_|\__|_|\___/|_| |_|                                     
                                                                                                    
 _   _                __     ___                                                                    
| \ | | _____      __ \ \   / (_) _____      __                                                     
|  \| |/ _ \ \ /\ / /  \ \ / /| |/ _ \ \ /\ / /                                                     
| |\  |  __/\ V  V /    \ V / | |  __/\ V  V /                                                      
|_| \_|\___| \_/\_/      \_/  |_|\___| \_/\_/

"""

@require_http_methods(["GET"])
def OCIAParticipantAccessConfirmationNewView(request:HttpRequest, code:str) -> HttpResponse:
    url_code = code
    saved_code = request.session.get("participant_access_code", '')
    request.session.pop("participant_access_code", None)
    if saved_code == url_code:
        return redirect('OCIAParticipantCreateView')
    else:
        request.session["participant_error_message"] = "Access denied."
        return redirect('OCIAParticipantErrorView')

"""
  ___   ____ ___    _      ____            _   _      _                   _                         
 / _ \ / ___|_ _|  / \    |  _ \ __ _ _ __| |_(_) ___(_)_ __   __ _ _ __ | |_                       
| | | | |    | |  / _ \   | |_) / _` | '__| __| |/ __| | '_ \ / _` | '_ \| __|                      
| |_| | |___ | | / ___ \  |  __/ (_| | |  | |_| | (__| | |_) | (_| | | | | |_                       
 \___/ \____|___/_/   \_\ |_|   \__,_|_|   \__|_|\___|_| .__/ \__,_|_| |_|\__|                      
                                                       |_|                                          
  ____                _        __     ___                                                           
 / ___|_ __ ___  __ _| |_ ___  \ \   / (_) _____      __                                            
| |   | '__/ _ \/ _` | __/ _ \  \ \ / /| |/ _ \ \ /\ / /                                            
| |___| | |  __/ (_| | ||  __/   \ V / | |  __/\ V  V /                                             
 \____|_|  \___|\__,_|\__\___|    \_/  |_|\___| \_/\_/                                              
                                                                                                    
                                                                                                    
"""

@require_http_methods(["GET", "POST"])
def OCIAParticipantCreateView(request: HttpRequest) -> HttpResponse:
    view = OCIAParticipantView(request)
    participant_create_enabled = request.session.get('participant_create_enabled', False)
    if not participant_create_enabled:
        return view.not_logged_in_error()
    if request.method == "POST":
        form = f.OCIAParticipantForm(request.POST)
    else:
        data = dict(email=request.session.pop('participant_email', ''))
        form = f.OCIAParticipantForm(initial=data)
    if request.method == "POST" and form.is_valid():
        request.session.pop('participant_create_enabled', False)
        participant:m.OCIAParticipant = form.save(commit=False)
        # hashlib.sha256(secrets.token_bytes(32)).hexdigest()[0:32]
        email = str(participant.email).lower()
        if m.OCIAParticipant.objects.filter(email__iexact=email).exists():
            return view.error(f'The specified email address <strong>{email}</strong> is already in use. Do you want to <a href="{reverse("OCIAParticipantLoginView")}">login</a>?')
        participant.liturgical_year = view.app_settings.liturgical_year
        participant.save()
        request.session["participant_id"] = participant.id
        return redirect("OCIAParticipantReligionCreateView")
    context = {
        "form": form,
        "site": view.site_settings,
    }
    return render(request, "ocia/ocia-participant-create-form.html", context)

'''
   ___   ____ ___    _      ____            _   _      _                   _    
  / _ \ / ___|_ _|  / \    |  _ \ __ _ _ __| |_(_) ___(_)_ __   __ _ _ __ | |_  
 | | | | |    | |  / _ \   | |_) / _` | '__| __| |/ __| | '_ \ / _` | '_ \| __| 
 | |_| | |___ | | / ___ \  |  __/ (_| | |  | |_| | (__| | |_) | (_| | | | | |_  
  \___/ \____|___/_/   \_\ |_|   \__,_|_|   \__|_|\___|_| .__/ \__,_|_| |_|\__| 
  _   _           _       _        __     ___           |_|                     
 | | | |_ __   __| | __ _| |_ ___  \ \   / (_) _____      __                    
 | | | | '_ \ / _` |/ _` | __/ _ \  \ \ / /| |/ _ \ \ /\ / /                    
 | |_| | |_) | (_| | (_| | ||  __/   \ V / | |  __/\ V  V /                     
  \___/| .__/ \__,_|\__,_|\__\___|    \_/  |_|\___| \_/\_/                      
       |_|                                                                      
'''

@require_http_methods(["GET", "POST"])
def OCIAParticipantUpdateView(request:HttpRequest) -> HttpResponse:
    view = OCIAParticipantView(request)
    if view.participant is None: return view.not_logged_in_error()
    if not view.enable_editing: return view.editing_disabled_error()
    form = f.OCIAParticipantForm(request.POST or None, instance=view.participant)
    if request.method == "POST" and form.is_valid():
        if "save" in request.POST:
            form.save()
        return redirect("OCIAParticipantNavigationView")
    context = {
        "form": form,
        "site": view.site_settings,
    }
    return render(request, "ocia/ocia-participant-update-form.html", context)

"""
  ___   ____ ___    _      ____            _   _      _                   _                         
 / _ \ / ___|_ _|  / \    |  _ \ __ _ _ __| |_(_) ___(_)_ __   __ _ _ __ | |_                       
| | | | |    | |  / _ \   | |_) / _` | '__| __| |/ __| | '_ \ / _` | '_ \| __|                      
| |_| | |___ | | / ___ \  |  __/ (_| | |  | |_| | (__| | |_) | (_| | | | | |_                       
 \___/ \____|___/_/   \_\ |_|   \__,_|_|   \__|_|\___|_| .__/ \__,_|_| |_|\__|                      
                                                       |_|                                          
 ____      _ _       _                ____                _                                         
|  _ \ ___| (_) __ _(_) ___  _ __    / ___|_ __ ___  __ _| |_ ___                                   
| |_) / _ \ | |/ _` | |/ _ \| '_ \  | |   | '__/ _ \/ _` | __/ _ \                                  
|  _ <  __/ | | (_| | | (_) | | | | | |___| | |  __/ (_| | ||  __/                                  
|_| \_\___|_|_|\__, |_|\___/|_| |_|  \____|_|  \___|\__,_|\__\___|                                  
               |___/                                                                                
__     ___                                                                                          
\ \   / (_) _____      __                                                                           
 \ \ / /| |/ _ \ \ /\ / /                                                                           
  \ V / | |  __/\ V  V /                                                                            
   \_/  |_|\___| \_/\_/

"""

@require_http_methods(["GET", "POST"])
def OCIAParticipantReligionCreateView(request:HttpRequest) -> HttpResponse:
    view = OCIAParticipantView(request)
    if view.participant is None: return view.not_logged_in_error()
    if not view.enable_editing: return view.editing_disabled_error()
    form = f.OCIAParticipantReligionForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.instance.participant_id = view.participant_id
        form.save()
        try:
            num_marriages = int(str(view.participant.num_marriages).strip())
        except (ValueError, TypeError):
            num_marriages = 0
        if view.participant.engaged == "yes":
            return redirect("OCIAParticipantEngagementCreateView")
        elif num_marriages > 0 or view.participant.marital_status == "married":
            return redirect("OCIAParticipantMarriageCreateView")
        return redirect("OCIAParticipantParentCreateView")
    context = {
        "form": form,
        "site": view.site_settings
    }
    return render(request, "ocia/ocia-participant-religion-create-form.html", context)

"""
  ___   ____ ___    _      ____            _   _      _                   _                         
 / _ \ / ___|_ _|  / \    |  _ \ __ _ _ __| |_(_) ___(_)_ __   __ _ _ __ | |_                       
| | | | |    | |  / _ \   | |_) / _` | '__| __| |/ __| | '_ \ / _` | '_ \| __|                      
| |_| | |___ | | / ___ \  |  __/ (_| | |  | |_| | (__| | |_) | (_| | | | | |_                       
 \___/ \____|___/_/   \_\ |_|   \__,_|_|   \__|_|\___|_| .__/ \__,_|_| |_|\__|                      
                                                       |_|                                          
 ____      _ _       _               _   _           _       _                                      
|  _ \ ___| (_) __ _(_) ___  _ __   | | | |_ __   __| | __ _| |_ ___                                
| |_) / _ \ | |/ _` | |/ _ \| '_ \  | | | | '_ \ / _` |/ _` | __/ _ \                               
|  _ <  __/ | | (_| | | (_) | | | | | |_| | |_) | (_| | (_| | ||  __/                               
|_| \_\___|_|_|\__, |_|\___/|_| |_|  \___/| .__/ \__,_|\__,_|\__\___|                               
               |___/                      |_|                                                       
__     ___                                                                                          
\ \   / (_) _____      __                                                                           
 \ \ / /| |/ _ \ \ /\ / /                                                                           
  \ V / | |  __/\ V  V /                                                                            
   \_/  |_|\___| \_/\_/

"""

@require_http_methods(["GET", "POST"])
def OCIAParticipantReligionUpdateView(request:HttpRequest) -> HttpResponse:
    view = OCIAParticipantView(request)
    if view.participant is None: return view.not_logged_in_error()
    if not view.enable_editing: return view.editing_disabled_error()
    religion_record = get_object_or_404(m.OCIAParticipantReligion, participant_id=view.participant_id)
    form = f.OCIAParticipantReligionForm(request.POST or None, instance=religion_record)
    if request.method == "POST" and form.is_valid():
        if "save" in request.POST:
            form.save()
        return redirect("OCIAParticipantNavigationView")
    context = {
        "form": form,
        "site": view.site_settings,
    }
    return render(request, "ocia/ocia-participant-religion-update-form.html", context)

"""
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
  ____                _        __     ___                                                           
 / ___|_ __ ___  __ _| |_ ___  \ \   / (_) _____      __                                            
| |   | '__/ _ \/ _` | __/ _ \  \ \ / /| |/ _ \ \ /\ / /                                            
| |___| | |  __/ (_| | ||  __/   \ V / | |  __/\ V  V /                                             
 \____|_|  \___|\__,_|\__\___|    \_/  |_|\___| \_/\_/

"""

@require_http_methods(["GET", "POST"])
def OCIAParticipantEngagementCreateView(request:HttpRequest) -> HttpResponse:
    view = OCIAParticipantView(request)
    if view.participant is None: return view.not_logged_in_error()
    if not view.enable_editing: return view.editing_disabled_error()
    form = f.OCIAParticipantEngagementForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.instance.participant_id = view.participant_id
        form.save()
        return redirect("OCIAParticipantMarriageCreateView")
    context = {
        "form": form,
        "site": view.site_settings
    }
    return render(request, "ocia/ocia-participant-engagement-create-form.html", context)

"""
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
    _       _     _  __     ___                                                                     
   / \   __| | __| | \ \   / (_) _____      __                                                      
  / _ \ / _` |/ _` |  \ \ / /| |/ _ \ \ /\ / /                                                      
 / ___ \ (_| | (_| |   \ V / | |  __/\ V  V /                                                       
/_/   \_\__,_|\__,_|    \_/  |_|\___| \_/\_/

"""

@require_http_methods(["GET", "POST"])
def OCIAParticipantEngagementAddView(request:HttpRequest) -> HttpResponse:
    view = OCIAParticipantView(request)
    if view.participant is None: return view.not_logged_in_error()
    if not view.enable_editing: return view.editing_disabled_error()
    form = f.OCIAParticipantEngagementForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        if "save" in request.POST:
            form.instance.participant_id = view.participant_id
            form.save()
        return redirect("OCIAParticipantNavigationView")
    context = {
        "form": form,
        "site": SiteSettings.fetch()
    }
    return render(request, "ocia/ocia-participant-engagement-add-form.html", context)

"""
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
 _   _           _       _        __     ___                                                        
| | | |_ __   __| | __ _| |_ ___  \ \   / (_) _____      __                                         
| | | | '_ \ / _` |/ _` | __/ _ \  \ \ / /| |/ _ \ \ /\ / /                                         
| |_| | |_) | (_| | (_| | ||  __/   \ V / | |  __/\ V  V /                                          
 \___/| .__/ \__,_|\__,_|\__\___|    \_/  |_|\___| \_/\_/                                           
      |_|

"""

@require_http_methods(["GET", "POST"])
def OCIAParticipantEngagementUpdateView(request:HttpRequest) -> HttpResponse:
    view = OCIAParticipantView(request)
    if view.participant is None: return view.not_logged_in_error()
    if not view.enable_editing: return view.editing_disabled_error()
    engagement_record = get_object_or_404(m.OCIAParticipantEngagement, participant_id=view.participant_id)
    form = f.OCIAParticipantEngagementForm(request.POST or None, instance=engagement_record)
    if request.method == "POST" and form.is_valid():
        if "save" in request.POST:
            form.save()
        return redirect("OCIAParticipantNavigationView")
    context = {
        "form": form,
        "site": view.site_settings
    }
    return render(request, "ocia/ocia-participant-engagement-update-form.html", context)

"""
  ___   ____ ___    _      ____            _   _      _                   _                         
 / _ \ / ___|_ _|  / \    |  _ \ __ _ _ __| |_(_) ___(_)_ __   __ _ _ __ | |_                       
| | | | |    | |  / _ \   | |_) / _` | '__| __| |/ __| | '_ \ / _` | '_ \| __|                      
| |_| | |___ | | / ___ \  |  __/ (_| | |  | |_| | (__| | |_) | (_| | | | | |_                       
 \___/ \____|___/_/   \_\ |_|   \__,_|_|   \__|_|\___|_| .__/ \__,_|_| |_|\__|                      
                                                       |_|                                          
 __  __                 _                     ____                _                                 
|  \/  | __ _ _ __ _ __(_) __ _  __ _  ___   / ___|_ __ ___  __ _| |_ ___                           
| |\/| |/ _` | '__| '__| |/ _` |/ _` |/ _ \ | |   | '__/ _ \/ _` | __/ _ \                          
| |  | | (_| | |  | |  | | (_| | (_| |  __/ | |___| | |  __/ (_| | ||  __/                          
|_|  |_|\__,_|_|  |_|  |_|\__,_|\__, |\___|  \____|_|  \___|\__,_|\__\___|                          
                                |___/                                                               
__     ___                                                                                          
\ \   / (_) _____      __                                                                           
 \ \ / /| |/ _ \ \ /\ / /                                                                           
  \ V / | |  __/\ V  V /                                                                            
   \_/  |_|\___| \_/\_/

"""

@require_http_methods(["GET", "POST"])
def OCIAParticipantMarriageCreateView(request:HttpRequest) -> HttpResponse:
    view = OCIAParticipantView(request)
    if view.participant is None: return view.not_logged_in_error()
    if not view.enable_editing: return view.editing_disabled_error()
    form = f.OCIAParticipantMarriageForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.instance.participant_id = view.participant_id
        form.save()
        if "add_another" in request.POST:
            return redirect("OCIAParticipantMarriageCreateView")
        return redirect("OCIAParticipantParentCreateView")
    context = {
        "form": form,
        "site": view.site_settings
    }
    return render(request, "ocia/ocia-participant-marriage-create-form.html", context)

"""
  ___   ____ ___    _      ____            _   _      _                   _                         
 / _ \ / ___|_ _|  / \    |  _ \ __ _ _ __| |_(_) ___(_)_ __   __ _ _ __ | |_                       
| | | | |    | |  / _ \   | |_) / _` | '__| __| |/ __| | '_ \ / _` | '_ \| __|                      
| |_| | |___ | | / ___ \  |  __/ (_| | |  | |_| | (__| | |_) | (_| | | | | |_                       
 \___/ \____|___/_/   \_\ |_|   \__,_|_|   \__|_|\___|_| .__/ \__,_|_| |_|\__|                      
                                                       |_|                                          
 __  __                 _                       _       _     _                                     
|  \/  | __ _ _ __ _ __(_) __ _  __ _  ___     / \   __| | __| |                                    
| |\/| |/ _` | '__| '__| |/ _` |/ _` |/ _ \   / _ \ / _` |/ _` |                                    
| |  | | (_| | |  | |  | | (_| | (_| |  __/  / ___ \ (_| | (_| |                                    
|_|  |_|\__,_|_|  |_|  |_|\__,_|\__, |\___| /_/   \_\__,_|\__,_|                                    
                                |___/                                                               
__     ___                                                                                          
\ \   / (_) _____      __                                                                           
 \ \ / /| |/ _ \ \ /\ / /                                                                           
  \ V / | |  __/\ V  V /                                                                            
   \_/  |_|\___| \_/\_/

"""

@require_http_methods(["GET", "POST"])
def OCIAParticipantMarriageAddView(request:HttpRequest) -> HttpResponse:
    view = OCIAParticipantView(request)
    if view.participant is None: return view.not_logged_in_error()
    if not view.enable_editing: return view.editing_disabled_error()
    form = f.OCIAParticipantMarriageForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        if "save" in request.POST:
            form.instance.participant_id = view.participant_id
            form.save()
        return redirect("OCIAParticipantNavigationView")
    context = {
        "form": form,
        "site": SiteSettings.fetch()
    }
    return render(request, "ocia/ocia-participant-marriage-update-form.html", context)

"""
  ___   ____ ___    _      ____            _   _      _                   _                         
 / _ \ / ___|_ _|  / \    |  _ \ __ _ _ __| |_(_) ___(_)_ __   __ _ _ __ | |_                       
| | | | |    | |  / _ \   | |_) / _` | '__| __| |/ __| | '_ \ / _` | '_ \| __|                      
| |_| | |___ | | / ___ \  |  __/ (_| | |  | |_| | (__| | |_) | (_| | | | | |_                       
 \___/ \____|___/_/   \_\ |_|   \__,_|_|   \__|_|\___|_| .__/ \__,_|_| |_|\__|                      
                                                       |_|                                          
 __  __                 _                    _   _           _       _                              
|  \/  | __ _ _ __ _ __(_) __ _  __ _  ___  | | | |_ __   __| | __ _| |_ ___                        
| |\/| |/ _` | '__| '__| |/ _` |/ _` |/ _ \ | | | | '_ \ / _` |/ _` | __/ _ \                       
| |  | | (_| | |  | |  | | (_| | (_| |  __/ | |_| | |_) | (_| | (_| | ||  __/                       
|_|  |_|\__,_|_|  |_|  |_|\__,_|\__, |\___|  \___/| .__/ \__,_|\__,_|\__\___|                       
                                |___/             |_|                                               
__     ___                                                                                          
\ \   / (_) _____      __                                                                           
 \ \ / /| |/ _ \ \ /\ / /                                                                           
  \ V / | |  __/\ V  V /                                                                            
   \_/  |_|\___| \_/\_/

"""

@require_http_methods(["GET", "POST"])
def OCIAParticipantMarriageUpdateView(request:HttpRequest, pk:int) -> HttpResponse:
    view = OCIAParticipantView(request)
    if view.participant is None: return view.not_logged_in_error()
    if not view.enable_editing: return view.editing_disabled_error()
    marriage_record = get_object_or_404(
        m.OCIAParticipantMarriage,
        pk=pk,
        participant_id=view.participant_id
    )
    form = f.OCIAParticipantMarriageForm(request.POST or None, instance=marriage_record)
    if request.method == "POST" and form.is_valid():
        if "save" in request.POST:
            form.save()
        return redirect("OCIAParticipantNavigationView")
    context = {
        "form": form,
        "site": view.site_settings
    }
    return render(request, "ocia/ocia-participant-marriage-update-form.html", context)

"""
  ___   ____ ___    _      ____            _   _      _                   _                         
 / _ \ / ___|_ _|  / \    |  _ \ __ _ _ __| |_(_) ___(_)_ __   __ _ _ __ | |_                       
| | | | |    | |  / _ \   | |_) / _` | '__| __| |/ __| | '_ \ / _` | '_ \| __|                      
| |_| | |___ | | / ___ \  |  __/ (_| | |  | |_| | (__| | |_) | (_| | | | | |_                       
 \___/ \____|___/_/   \_\ |_|   \__,_|_|   \__|_|\___|_| .__/ \__,_|_| |_|\__|                      
                                                       |_|                                          
 ____                      _      ____                _                                             
|  _ \ __ _ _ __ ___ _ __ | |_   / ___|_ __ ___  __ _| |_ ___                                       
| |_) / _` | '__/ _ \ '_ \| __| | |   | '__/ _ \/ _` | __/ _ \                                      
|  __/ (_| | | |  __/ | | | |_  | |___| | |  __/ (_| | ||  __/                                      
|_|   \__,_|_|  \___|_| |_|\__|  \____|_|  \___|\__,_|\__\___|                                      
                                                                                                    
__     ___                                                                                          
\ \   / (_) _____      __                                                                           
 \ \ / /| |/ _ \ \ /\ / /                                                                           
  \ V / | |  __/\ V  V /                                                                            
   \_/  |_|\___| \_/\_/

"""

@require_http_methods(["GET", "POST"])
def OCIAParticipantParentCreateView(request:HttpRequest) -> HttpResponse:
    view = OCIAParticipantView(request)
    if view.participant is None: return view.not_logged_in_error()
    if not view.enable_editing: return view.editing_disabled_error()
    form = f.OCIAParticipantParentForm(request.POST or None)
    parent_count = view.participant.parents.count()
    if request.method == "POST" and form.is_valid():
        if str(form.instance.name).strip() == '':
            return redirect("OCIAParticipantQuestionsCreateView")
        form.instance.participant_id = view.participant_id
        form.save()
        if "add_another" in request.POST:
            return redirect("OCIAParticipantParentCreateView")
        return redirect("OCIAParticipantQuestionsCreateView")
    context = {
        "form": form,
        "parent_count": parent_count,
        "site": view.site_settings
    }
    return render(request, "ocia/ocia-participant-parent-create-form.html", context)

"""
  ___   ____ ___    _      ____            _   _      _                   _                         
 / _ \ / ___|_ _|  / \    |  _ \ __ _ _ __| |_(_) ___(_)_ __   __ _ _ __ | |_                       
| | | | |    | |  / _ \   | |_) / _` | '__| __| |/ __| | '_ \ / _` | '_ \| __|                      
| |_| | |___ | | / ___ \  |  __/ (_| | |  | |_| | (__| | |_) | (_| | | | | |_                       
 \___/ \____|___/_/   \_\ |_|   \__,_|_|   \__|_|\___|_| .__/ \__,_|_| |_|\__|                      
                                                       |_|                                          
 ____                      _        _       _     _  __     ___                                     
|  _ \ __ _ _ __ ___ _ __ | |_     / \   __| | __| | \ \   / (_) _____      __                      
| |_) / _` | '__/ _ \ '_ \| __|   / _ \ / _` |/ _` |  \ \ / /| |/ _ \ \ /\ / /                      
|  __/ (_| | | |  __/ | | | |_   / ___ \ (_| | (_| |   \ V / | |  __/\ V  V /                       
|_|   \__,_|_|  \___|_| |_|\__| /_/   \_\__,_|\__,_|    \_/  |_|\___| \_/\_/

"""

@require_http_methods(["GET", "POST"])
def OCIAParticipantParentAddView(request:HttpRequest) -> HttpResponse:
    view = OCIAParticipantView(request)
    if view.participant is None: return view.not_logged_in_error()
    if not view.enable_editing: return view.editing_disabled_error()
    form = f.OCIAParticipantParentForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        if "save" in request.POST:
            form.instance.participant_id = view.participant_id
            form.save()
        return redirect("OCIAParticipantNavigationView")
    context = {
        "form": form,
        "site": view.site_settings
    }
    return render(request, "ocia/ocia-participant-parent-update-form.html", context)
"""
  ___   ____ ___    _      ____            _   _      _                   _                         
 / _ \ / ___|_ _|  / \    |  _ \ __ _ _ __| |_(_) ___(_)_ __   __ _ _ __ | |_                       
| | | | |    | |  / _ \   | |_) / _` | '__| __| |/ __| | '_ \ / _` | '_ \| __|                      
| |_| | |___ | | / ___ \  |  __/ (_| | |  | |_| | (__| | |_) | (_| | | | | |_                       
 \___/ \____|___/_/   \_\ |_|   \__,_|_|   \__|_|\___|_| .__/ \__,_|_| |_|\__|                      
                                                       |_|                                          
 ____                      _     _   _           _       _                                          
|  _ \ __ _ _ __ ___ _ __ | |_  | | | |_ __   __| | __ _| |_ ___                                    
| |_) / _` | '__/ _ \ '_ \| __| | | | | '_ \ / _` |/ _` | __/ _ \                                   
|  __/ (_| | | |  __/ | | | |_  | |_| | |_) | (_| | (_| | ||  __/                                   
|_|   \__,_|_|  \___|_| |_|\__|  \___/| .__/ \__,_|\__,_|\__\___|                                   
                                      |_|                                                           
__     ___                                                                                          
\ \   / (_) _____      __                                                                           
 \ \ / /| |/ _ \ \ /\ / /                                                                           
  \ V / | |  __/\ V  V /                                                                            
   \_/  |_|\___| \_/\_/

"""

@require_http_methods(["GET", "POST"])
def OCIAParticipantParentUpdateView(request:HttpRequest, pk:int) -> HttpResponse:
    view = OCIAParticipantView(request)
    if view.participant is None: return view.not_logged_in_error()
    if not view.enable_editing: return view.editing_disabled_error()
    parent_record = get_object_or_404(
        m.OCIAParticipantParent,
        pk=pk,
        participant_id=view.participant_id
    )
    form = f.OCIAParticipantParentForm(request.POST or None, instance=parent_record)
    if request.method == "POST" and form.is_valid():
        if "save" in request.POST:
            form.save()
        return redirect("OCIAParticipantNavigationView")
    context = {
        "form": form,
        "site": view.site_settings
    }
    return render(request, "ocia/ocia-participant-parent-update-form.html", context)

"""
  ___   ____ ___    _      ____            _   _      _                   _                         
 / _ \ / ___|_ _|  / \    |  _ \ __ _ _ __| |_(_) ___(_)_ __   __ _ _ __ | |_                       
| | | | |    | |  / _ \   | |_) / _` | '__| __| |/ __| | '_ \ / _` | '_ \| __|                      
| |_| | |___ | | / ___ \  |  __/ (_| | |  | |_| | (__| | |_) | (_| | | | | |_                       
 \___/ \____|___/_/   \_\ |_|   \__,_|_|   \__|_|\___|_| .__/ \__,_|_| |_|\__|                      
                                                       |_|                                          
  ___                  _   _                    ____                _                               
 / _ \ _   _  ___  ___| |_(_) ___  _ __  ___   / ___|_ __ ___  __ _| |_ ___                         
| | | | | | |/ _ \/ __| __| |/ _ \| '_ \/ __| | |   | '__/ _ \/ _` | __/ _ \                        
| |_| | |_| |  __/\__ \ |_| | (_) | | | \__ \ | |___| | |  __/ (_| | ||  __/                        
 \__\_\\__,_|\___||___/\__|_|\___/|_| |_|___/  \____|_|  \___|\__,_|\__\___|                        
                                                                                                    
__     ___                                                                                          
\ \   / (_) _____      __                                                                           
 \ \ / /| |/ _ \ \ /\ / /                                                                           
  \ V / | |  __/\ V  V /                                                                            
   \_/  |_|\___| \_/\_/

"""

@require_http_methods(["GET", "POST"])
def OCIAParticipantQuestionsCreateView(request:HttpRequest) -> HttpResponse:
    view = OCIAParticipantView(request)
    if view.participant is None: return view.not_logged_in_error()
    if not view.enable_editing: return view.editing_disabled_error()
    existing_record = m.OCIAParticipantQuestions.objects.filter(participant_id=view.participant_id).first()
    form = f.OCIAParticipantQuestionsForm(request.POST or None, instance=existing_record)
    if request.method == "POST" and form.is_valid():
        form.instance.participant_id = view.participant_id
        form.save()
        return redirect("OCIAParticipantNavigationView")
    context = {
        "form": form,
        "site": view.site_settings
    }
    return render(request, "ocia/ocia-participant-questions-create-form.html", context)

"""
  ___   ____ ___    _      ____            _   _      _                   _                         
 / _ \ / ___|_ _|  / \    |  _ \ __ _ _ __| |_(_) ___(_)_ __   __ _ _ __ | |_                       
| | | | |    | |  / _ \   | |_) / _` | '__| __| |/ __| | '_ \ / _` | '_ \| __|                      
| |_| | |___ | | / ___ \  |  __/ (_| | |  | |_| | (__| | |_) | (_| | | | | |_                       
 \___/ \____|___/_/   \_\ |_|   \__,_|_|   \__|_|\___|_| .__/ \__,_|_| |_|\__|                      
                                                       |_|                                          
  ___                  _   _                   _   _           _       _                            
 / _ \ _   _  ___  ___| |_(_) ___  _ __  ___  | | | |_ __   __| | __ _| |_ ___                      
| | | | | | |/ _ \/ __| __| |/ _ \| '_ \/ __| | | | | '_ \ / _` |/ _` | __/ _ \                     
| |_| | |_| |  __/\__ \ |_| | (_) | | | \__ \ | |_| | |_) | (_| | (_| | ||  __/                     
 \__\_\\__,_|\___||___/\__|_|\___/|_| |_|___/  \___/| .__/ \__,_|\__,_|\__\___|                     
                                                    |_|                                             
__     ___                                                                                          
\ \   / (_) _____      __                                                                           
 \ \ / /| |/ _ \ \ /\ / /                                                                           
  \ V / | |  __/\ V  V /                                                                            
   \_/  |_|\___| \_/\_/

"""

@require_http_methods(["GET", "POST"])
def OCIAParticipantQuestionsUpdateView(request:HttpRequest) -> HttpResponse:
    view = OCIAParticipantView(request)
    if view.participant is None: return view.not_logged_in_error()
    if not view.enable_editing: return view.editing_disabled_error()
    questions_record = get_object_or_404(
        m.OCIAParticipantQuestions,
        participant_id=view.participant_id
    )
    form = f.OCIAParticipantQuestionsForm(request.POST or None, instance=questions_record)
    if request.method == "POST" and form.is_valid():
        if "save" in request.POST:
            form.save()
        return redirect("OCIAParticipantNavigationView")
    context = {
        "form": form,
        "site": view.site_settings
    }
    return render(request, "ocia/ocia-participant-questions-update-form.html", context)

"""
  ___   ____ ___    _      ____            _   _      _                   _                         
 / _ \ / ___|_ _|  / \    |  _ \ __ _ _ __| |_(_) ___(_)_ __   __ _ _ __ | |_                       
| | | | |    | |  / _ \   | |_) / _` | '__| __| |/ __| | '_ \ / _` | '_ \| __|                      
| |_| | |___ | | / ___ \  |  __/ (_| | |  | |_| | (__| | |_) | (_| | | | | |_                       
 \___/ \____|___/_/   \_\ |_|   \__,_|_|   \__|_|\___|_| .__/ \__,_|_| |_|\__|                      
                                                       |_|                                          
 _____                      __     ___                                                              
| ____|_ __ _ __ ___  _ __  \ \   / (_) _____      __                                               
|  _| | '__| '__/ _ \| '__|  \ \ / /| |/ _ \ \ /\ / /                                               
| |___| |  | | | (_) | |      \ V / | |  __/\ V  V /                                                
|_____|_|  |_|  \___/|_|       \_/  |_|\___| \_/\_/

"""

@require_GET
def OCIAParticipantErrorView(request:HttpRequest) -> HttpResponse:
    message = request.session.pop("participant_error_message", 'An unspecified error occurred.')
    context = {
        "message": message,
        "site": SiteSettings.fetch(),
    }
    return render(request, "ocia/ocia-participant-error.html", context)

"""
  ___   ____ ___    _      ____            _   _      _                   _                         
 / _ \ / ___|_ _|  / \    |  _ \ __ _ _ __| |_(_) ___(_)_ __   __ _ _ __ | |_                       
| | | | |    | |  / _ \   | |_) / _` | '__| __| |/ __| | '_ \ / _` | '_ \| __|                      
| |_| | |___ | | / ___ \  |  __/ (_| | |  | |_| | (__| | |_) | (_| | | | | |_                       
 \___/ \____|___/_/   \_\ |_|   \__,_|_|   \__|_|\___|_| .__/ \__,_|_| |_|\__|                      
                                                       |_|                                          
 _   _             _             _   _              __     ___                                      
| \ | | __ ___   _(_) __ _  __ _| |_(_) ___  _ __   \ \   / (_) _____      __                       
|  \| |/ _` \ \ / / |/ _` |/ _` | __| |/ _ \| '_ \   \ \ / /| |/ _ \ \ /\ / /                       
| |\  | (_| |\ V /| | (_| | (_| | |_| | (_) | | | |   \ V / | |  __/\ V  V /                        
|_| \_|\__,_| \_/ |_|\__, |\__,_|\__|_|\___/|_| |_|    \_/  |_|\___| \_/\_/                         
                     |___/

"""

@require_GET
def OCIAParticipantNavigationView(request:HttpRequest) -> HttpResponse:
    view = OCIAParticipantView(request)
    if view.participant is None: return view.not_logged_in_error()
    if not view.enable_editing: return view.editing_disabled_error()
    context = {
        "participant": view.participant,
        "site": view.site_settings
    }
    return render(request, "ocia/ocia-participant-navigation.html", context)

@require_GET
def OCIAParticipantNavigationOrStartView(request:HttpRequest) -> HttpResponse:
    view = OCIAParticipantView(request)
    if view.participant is None: 
        return redirect('OCIAParticipantStartView')
    if not view.enable_editing: return view.editing_disabled_error()
    context = {
        "participant": view.participant,
        "site": view.site_settings
    }
    return render(request, "ocia/ocia-participant-navigation.html", context)

"""
  ___   ____ ___    _      ____            _   _      _                   _                         
 / _ \ / ___|_ _|  / \    |  _ \ __ _ _ __| |_(_) ___(_)_ __   __ _ _ __ | |_                       
| | | | |    | |  / _ \   | |_) / _` | '__| __| |/ __| | '_ \ / _` | '_ \| __|                      
| |_| | |___ | | / ___ \  |  __/ (_| | |  | |_| | (__| | |_) | (_| | | | | |_                       
 \___/ \____|___/_/   \_\ |_|   \__,_|_|   \__|_|\___|_| .__/ \__,_|_| |_|\__|                      
                                                       |_|                                          
 ____       _      _         ____                        _                                          
|  _ \  ___| | ___| |_ ___  |  _ \ ___  ___ ___  _ __ __| |                                         
| | | |/ _ \ |/ _ \ __/ _ \ | |_) / _ \/ __/ _ \| '__/ _` |                                         
| |_| |  __/ |  __/ ||  __/ |  _ <  __/ (_| (_) | | | (_| |                                         
|____/ \___|_|\___|\__\___| |_| \_\___|\___\___/|_|  \__,_|                                         
                                                                                                    
__     ___                                                                                          
\ \   / (_) _____      __                                                                           
 \ \ / /| |/ _ \ \ /\ / /                                                                           
  \ V / | |  __/\ V  V /                                                                            
   \_/  |_|\___| \_/\_/

"""

@require_GET
def OCIAParticipantDeleteRecordView(request:HttpRequest, category:str, id:str) -> HttpResponse:
    view = OCIAParticipantView(request)
    if view.participant is None: return view.not_logged_in_error()
    if not view.enable_editing: return view.editing_disabled_error()
    if category == 'parent':
        parent = get_object_or_404(m.OCIAParticipantParent, id=id)
        parent.delete()
    if category == 'engagement':
        engagement = get_object_or_404(m.OCIAParticipantEngagement, id=id)
        engagement.delete()
    if category == 'marriage':
        marriage = get_object_or_404(m.OCIAParticipantMarriage, id=id)
        marriage.delete()
    return redirect('OCIAParticipantNavigationView')

@require_GET
def OCIAParticipantDeleteRecordNoArgView(request:HttpRequest) -> None:
    view = OCIAParticipantView(request)
    return view.error('Invalid request.')