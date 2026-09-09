# Sacred Heart Forms: AI Working Overview

> Purpose: a compact, code-grounded knowledge base for AI-assisted maintenance. Search this file by the headings, symbols, route names, model names, or task keywords below. Re-check the referenced source before changing behavior: this is a retrieval map, not a replacement for the code.
>
> Snapshot reviewed: 2026-09-07. Primary application: `apps/ocia_participant`. Supporting applications: `apps/main` and `apps/maven`.

## 1. Executive summary

This repository is a Django 5.2.5 site whose public root is an OCIA (Order of Christian Initiation of Adults) participant registration and self-service editing workflow. A participant enters an email address, receives a one-time link, creates or opens a registration, and navigates among personal, religious, engagement, marriage, parent, and questionnaire records.

The OCIA workflow does **not** use Django's authenticated `User`. It treats a Django session key (`participant_id`) as the effective login. Email-link state is held in additional Django session keys. `OCIAParticipantSession` exists as a second, database-backed session concept, but the current authorization checks ultimately rely on `participant_id` and a corresponding participant row.

The application is a server-rendered monolith:

- Django function views handle GET/POST and redirects.
- `ModelForm` classes validate and render each registration section.
- Django templates extend a shared Bootstrap/jQuery base.
- SQLite is configured at `data/data.db3`.
- Site and OCIA behavior are controlled by singleton-like settings models in Django admin.
- SMTP sends passwordless access links.
- The bundled `maven` application is a separate media manager and is not part of the OCIA business flow.

## 2. Repository map and source-of-truth order

| Path | Responsibility | Read when |
|---|---|---|
| `proj/settings.py` | Installed apps, middleware, SQLite, static/media, SMTP, logging, environment selection | Runtime/config/deployment issues |
| `proj/config/dev.py`, `proj/config/prod.py` | Host-specific `DEBUG`, hosts, root URL, cookie flags | Environment differences |
| `proj/urls.py` | Top-level routing | Entry-point or prefix questions |
| `apps/ocia_participant/models.py` | OCIA choices, tables, relationships, derived properties | Schema/business meaning |
| `apps/ocia_participant/forms.py` | Public field exposure, widgets, validation, normalization | Input and validation behavior |
| `apps/ocia_participant/views.py` | Login/link flow, workflow branching, ownership gates, CRUD | Request behavior and security |
| `apps/ocia_participant/urls.py` | Named routes and route arguments | Navigation/reverse lookup |
| `apps/ocia_participant/templates/ocia/` | Pages, conditional field JS, submit-button contracts | UI and POST intent |
| `apps/ocia_participant/admin.py` | Staff data management and inline layout | Back-office behavior |
| `apps/ocia_participant/tests.py` | Small current regression suite | Existing intended behavior |
| `apps/main/models.py` | Global `SiteSettings` and computed theme colors | Branding/template context |
| `apps/main/templates/main/base.html` | Shared layout, CSS, JS `FieldManager`, flatpickr setup | Cross-form UI behavior |
| `apps/main/templates/main/form.html` | Generic field/help/error renderer | All ModelForm display |
| `apps/maven/` | Independent media library/explorer | Only media-related tasks |
| `lib/util.py` | Color helpers and random token helper | Theme/session token details |
| `lib/whisper.py` | Fernet decrypt/encrypt with embedded key | Credential/config security |

There are no migration files visible in this snapshot. Django therefore treats local apps as unmigrated and attempts table synchronization during tests.

## 3. Runtime topology

```text
Browser
  -> proj/urls.py
     -> /                         OCIAParticipantNavigationOrStartView
     -> /admin/                   Django admin
     -> /ocia/participant/...     apps/ocia_participant/urls.py
     -> /maven/...                media manager
  -> function view
  -> OCIAParticipantView helper loads SiteSettings + OCIAParticipantSettings
  -> ModelForm / ORM / Django session
  -> SQLite data/data.db3
  -> HTML template (or SMTP access email)
```

Python application packages live under `apps/`; `proj/settings.py` inserts that directory into `sys.path`, so imports usually use `main`, `maven`, and `ocia_participant` as top-level modules.

## 4. OCIA domain model

Relationship overview:

```text
OCIAParticipant
  |-- 0..1 OCIAParticipantReligion    related_name=religion, CASCADE
  |-- 0..1 OCIAParticipantEngagement  related_name=engagement, CASCADE
  |-- 0..1 OCIAParticipantQuestions   related_name=questions, CASCADE
  |-- 0..* OCIAParticipantMarriage    related_name=marriages, CASCADE
  |-- 0..* OCIAParticipantParent      related_name=parents, CASCADE
  `-- 0..* OCIAParticipantSession     related_name=session, CASCADE; participant nullable
```

### `OCIAParticipantSettings`

Global workflow configuration: `access_code`, `liturgical_year`, and `enable_editing`. `fetch()` gets or creates primary key 1. Admin prevents adding a second row and redirects the list page to the existing singleton. The `access_code` currently appears legacy/unrelated to emailed per-request codes; trace usage before relying on it.

### `OCIAParticipantSession`

Database audit/state for passwordless access: nullable participant FK, unique-ish token concepts (`uid`, `access_code`), email, state, expiry, creation time, client IP, user agent, `is_logged_in`, and `is_valid`. `is_expired()` returns true when invalid or past `expires_on`. View code deletes expired rows and creates/refreshes records with a three-day expiry.

Important: this model is not Django's session model. The browser's Django session is still the effective authorization state.

### `OCIAParticipant`

The registration root. Major fields are name and suffix/preferred name, liturgical year, created timestamp, email, phone/text permission, mailing address, birth date/place, sex, marital status, number of marriages, and engaged status. `age` is derived from date of birth; `full_name` is derived from name parts. Email is the lookup identity used by the login flow, even though code-level uniqueness must be checked before assuming database enforcement.

### Child records

- `OCIAParticipantReligion`: current affiliation, baptism status/denomination/date/details, sacraments of confession/communion/confirmation, and private `admin_notes`.
- `OCIAParticipantMarriage`: zero or more marriages with spouse, status, marriage/divorce dates, spouse-first-marriage flag, spouse religion, notes, and private `admin_notes`.
- `OCIAParticipantEngagement`: optional one-to-one fiancé/planned-marriage information, both parties' first-marriage flags, notes, and private `admin_notes`.
- `OCIAParticipantParent`: zero or more parent/guardian-style records with name, relationship/title, and religion. UI/admin conventions suggest at most two, but the database relationship itself is one-to-many.
- `OCIAParticipantQuestions`: optional one-to-one narrative answers about attending OCIA, prior religious education, questions/concerns, likelihood of becoming Catholic, and comments.

Choice enums in `models.py` centralize yes/no, unknown, sex, marital status, marriage status, denomination, religion, parent title, and becoming-Catholic answers. Preserve stored choice values when changing labels.

## 5. Forms and validation

All public ModelForms use `OCIAParticipantFormMixin`, which replaces RadioSelect choices with the model's explicit choices so Django does not inject a blank `---------` option.

| Form | Model | Excluded/non-public fields |
|---|---|---|
| `OCIAParticipantForm` | participant | `liturgical_year`, `created_on` |
| `OCIAParticipantReligionForm` | religion | `participant`, `admin_notes` |
| `OCIAParticipantMarriageForm` | marriage | `participant`, `admin_notes` |
| `OCIAParticipantEngagementForm` | engagement | `participant`, `admin_notes` |
| `OCIAParticipantParentForm` | parent | `participant` |
| `OCIAParticipantQuestionsForm` | questions | `participant` |

Dates use a text input with class `flatpickr`; the shared base initializes them with `Y-m-d`. Several choice fields render as radio groups.

Participant-specific cleaning trims required names/email, uses an additional email regex, accepts common US phone formats and normalizes them to `(###) ###-####`, rejects blank/non-numeric/negative marriage counts, and requires an engagement response for single participants. A known defect exists in `clean_phone`: the wrong-length branch constructs `forms.ValidationError(...)` but does not `raise` it.

Templates may hide irrelevant fields using JavaScript, but hidden fields are not automatically server-side policy. Whenever conditional requirements change, update model/form validation and tests—not only template logic.

## 6. Passwordless login and registration flow

### Existing participant

```text
GET / or /ocia/participant/participant
  -> login page
POST /ocia/participant/login with email
  -> case-insensitive participant lookup
  -> stash participant_id_temp, participant_access_code, participant_email
  -> /access/notification/existing sends link
  -> user opens /access/confirmation/existing/<code>
  -> compare URL code with session-held code
  -> promote participant_id_temp to participant_id
  -> navigation dashboard
```

### New participant

```text
POST login with unknown email
  -> stash participant_create_enabled, participant_access_code, participant_email
  -> /access/notification/new sends link
  -> /access/confirmation/new/<code>
  -> /create
  -> religion/create
  -> engagement/create only when participant.engaged == yes
  -> marriage/create only when num_marriages > 0
  -> parent/create (zero or multiple via buttons)
  -> questions/create
  -> navigation dashboard
```

The access link is bound to the same browser session because the expected code and temporary participant/email state live in `request.session`. Opening the email on another browser/device will not have the matching state. Generated URL codes are SHA-256-derived random hex strings in the active login flow; `generate_access_code()` separately creates a 10-character code for `OCIAParticipantSession`.

In debug mode, or for an address ending `@fake.com`, notification pages expose a fake/debug path rather than requiring live mail behavior. Review the templates before changing this development convenience.

## 7. Session and authorization contract

`OCIAParticipantView` is a per-request helper, not a Django class-based view. Its constructor fetches both settings singletons and loads `participant_id` from the Django session. If that ID resolves, `view.participant` represents the logged-in participant.

Known workflow session keys:

- `participant_id`: effective logged-in participant ID.
- `participant_id_temp`: existing participant pending link confirmation.
- `participant_access_code`: expected one-time URL code.
- `participant_create_enabled`: authorizes reaching participant creation.
- `participant_email`: email carried into creation/email sending.
- `participant_debug_mode`: development/fake-mail behavior.
- `participant_error_message`: flash-like error content consumed by the error page.
- `ocia_participant_session_uid`: database-session identifier; notably absent from `OCIAParticipantView.session_keys`, so `clear_session()` does not remove it.

Most create/update/navigation/delete views enforce both `view.participant is not None` and `OCIAParticipantSettings.enable_editing`. Creation is special: it is gated by `participant_create_enabled`, then sets `participant_id` after saving.

Security-critical invariant: every child-object update or delete must scope the query to `participant_id=view.participant_id`. Current update views do this with `get_object_or_404`. The generic delete view currently fetches parent/engagement/marriage by ID alone and therefore permits an authenticated participant to delete another participant's child row if its numeric ID is known. Fix this before exposing predictable IDs or treating the route as safe.

The delete endpoint is GET-only and mutates data. It should normally be a CSRF-protected POST and enforce ownership.

## 8. URL inventory

All names below are global (no app namespace). The included prefix is `/ocia/participant/`.

| Relative path | View/purpose |
|---|---|
| `participant` | start; redirects to login |
| `login` | email entry and lookup |
| `access/notification/existing` | send/render existing-user link notice |
| `access/notification/new` | send/render new-user link notice |
| `access/confirmation/existing/<code>` | validate link and log in |
| `access/confirmation/new/<code>` | validate link and allow create |
| `logout` | clear participant workflow session keys |
| `create`, `update` | participant root record |
| `religion/create`, `religion/update` | religion one-to-one |
| `engagement/create`, `engagement/add`, `engagement/update` | engagement one-to-one |
| `marriage/create`, `marriage/add`, `marriage/update/<pk>` | marriage collection |
| `parent/create`, `parent/add`, `parent/update/<pk>` | parent collection |
| `questions/create`, `questions/update` | questions one-to-one |
| `navigation` | self-service dashboard |
| `delete/<category>/<id>` | deletes parent, engagement, or marriage |
| `delete` | invalid-request error |
| `error` | consumes and displays session error |
| `test` | test page; reachable route |

Top-level `/` chooses the dashboard when `participant_id` resolves, otherwise redirects into login. `/main/` includes an empty URLconf. `/admin/` and `/maven/` are also mounted.

## 9. View conventions

Create views instantiate an unbound/bound form, assign `form.instance.participant_id`, save, then branch to the next wizard step. Add views save only when the POST contains a `save` button. Update views similarly save only on `save`; another submitted button effectively cancels and returns to navigation. Therefore button names in templates are part of the server contract.

For marriage/parent update, object retrieval includes both primary key and current participant ID. One-to-one updates retrieve by current participant ID. Create endpoints are not uniformly strict about pre-existing one-to-one rows: questions uses `.filter(...).first()` as its form instance, whereas other create paths should be checked for duplicate/IntegrityError behavior.

Errors are stored in session as HTML-containing strings and rendered by `ocia-participant-error.html`. Because several templates/fields use `|safe`, never put untrusted text into an error message without escaping.

## 10. Templates and front end

`apps/main/templates/main/base.html` owns the page shell, Bootstrap styling, theme CSS variables, jQuery, Font Awesome, dialog assets, flatpickr, and a generic `FieldManager`. Child forms override `{% block form-logic %}` to show/hide fields based on current answers. The generic `main/form.html` loops over fields and renders help/error text with `|safe`.

Each OCIA create/update template is intentionally separate even when it wraps the same form. This permits different headings, buttons, and wizard/navigation behavior. When adding a model field, inspect all create/update templates plus each form's `Meta.widgets` and conditional JS.

The navigation template uses related objects to show edit/add/delete actions for each registration section. It is the best UI-level index of which records are optional, singular, or repeatable.

Static dependencies are committed under `apps/main/static/main/site/vendor`; this is not an npm pipeline. Custom site CSS is `apps/main/static/main/site/css/site.css`. OCIA icon images are under `apps/ocia_participant/static/ocia/img/icon/`.

## 11. Admin behavior

`OCIAParticipantAdmin` shows religion, marriages, engagement, parents, and questions as stacked inlines; lists participants by year/name/email/phone and supports year filtering and name/email search. Admin constraints (`max_num` for parents/one-to-ones) guide staff UI but do not create database constraints. `OCIAParticipantSettings` is managed as a singleton. `SiteSettings` also enforces singleton behavior in `clean()`/`save()` and computes transient theme color attributes in `fetch()`.

## 12. Configuration and deployment assumptions

- Django version is pinned to 5.2.5 in both requirement files; local dependencies are fully pinned, server dependencies mostly are not.
- The database is SQLite at `BASE_DIR/data/data.db3`.
- Static output is `BASE_DIR/static`; uploaded media is `BASE_DIR/media` and is served through `static()` in the root URLconf.
- `TIME_ZONE = 'UTC'` with timezone-aware datetimes.
- Development versus production config is selected by `platform.node() == 'Kadura-5'`; every other hostname is treated as production.
- Production `HTTP_ROOT` is an HTTP IP while allowed hosts are domain names. Both dev and prod set secure session/CSRF cookies false.
- Debug toolbar is dynamically enabled when `DEBUG` and not running tests, but it is not listed in the provided requirements files.
- Settings import nonstandard modules (`fs`, and views import `ru` and `cronos`) that are not listed in requirements; they appear environment-provided.
- Logs target `logs/django.log` and `logs/ocia_participant.log`; the directory must already be usable during settings initialization/runtime.
- SMTP username/password ciphertext is committed in settings and decrypted using a Fernet key committed in `lib/whisper.py`. This is obfuscation, not secret separation. Rotate credentials and load secrets from the environment or a secret manager.
- `SECRET_KEY` is committed. Production must use a secret supplied outside source control.

## 13. Current verification baseline (2026-09-07)

`python manage.py check` fails with eight `fields.E120` errors because these `CharField`s lack `max_length`:

- `main.SiteSettings`: `title`, `icon`, `banner_bg_color`, `banner_fg_color`.
- `ocia_participant.OCIAParticipantSettings`: `access_code`, `liturgical_year`.
- `ocia_participant.OCIAParticipantSession`: `access_code`, `email`.

`python manage.py test` cannot create the SQLite test database and stops with `django.db.utils.OperationalError: near "None": syntax error`; this follows from invalid generated column SQL for the missing lengths. Consequently the existing test cases are not currently executing.

The OCIA tests cover only login GET, start/navigation redirects, session error display, and basic standalone email validation. They do not cover the full email-link flow, model forms, wizard branches, ownership, editing-disabled behavior, CRUD, email failures, expiration, or cross-browser behavior. `apps/maven/tests.py` is separate and much larger.

## 14. Risks and known defects, prioritized

### Critical/high

1. Cross-participant deletion: `OCIAParticipantDeleteRecordView` fetches child records only by ID, without participant ownership filtering.
2. Secrets in source: Django secret, Fernet key, and recoverable SMTP credentials are committed.
3. Production transport/cookies are insecure: configured HTTP root and both secure-cookie flags false.
4. Django system checks fail and tests cannot initialize due to eight invalid `CharField` declarations.

### Medium

1. Passwordless links only work in the browser session that requested them and appear replay-sensitive to session state rather than being independently signed database tokens.
2. Login identity depends on case-insensitive email lookup without an obvious database uniqueness constraint; duplicate emails can break `.get()` paths.
3. Mutating delete uses GET, making accidental activation and CSRF-style behavior possible.
4. HTML error strings and `|safe` rendering increase XSS risk if future messages interpolate user-controlled input.
5. `get_client_ip()` trusts the first `X-Forwarded-For` value without a trusted-proxy policy.
6. Hostname-based environment selection is brittle; unknown developer/CI hosts receive production settings.
7. Missing migrations prevent durable, reviewable schema evolution.

### Code-quality/maintenance

1. `clean_phone` fails to raise one constructed validation error.
2. `load_user_session()` has suspicious control flow: the no-email/no-UID branch accesses `self.user_session.is_valid` while `self.user_session` was initialized to `None`; the UID branch assigns `self.user_session.uid` before loading/creating an object. Exercise this path before building on it.
3. Several imports/functions are unused or duplicated in `views.py`, and `views.txt` appears to be a parallel artifact that can confuse searches.
4. Two test classes share the name `NavigationViewTests`, and coverage is very small.
5. AppConfig declares `name = 'ocia_participant'` while its file resides below `apps/`; this currently depends on `sys.path` manipulation.

## 15. Change recipes for AI assistants

### Add or change a participant field

1. Change `apps/ocia_participant/models.py` and preserve existing choice storage values.
2. Create a migration (after establishing migrations for the app).
3. Decide whether the public form exposes it; update `OCIAParticipantForm.Meta`, widgets, and cleaners.
4. Inspect both participant create/update templates and shared `main/form.html`/`base.html` logic.
5. Decide whether it belongs in admin list/search/filter.
6. Add model, form, create, update, and conditional-display tests.

### Add a new registration section

Update model + migration, form, create/update/add views as appropriate, URL names, templates, navigation links, admin inline, wizard redirect chain, ownership checks, and tests. Decide explicitly whether the relationship is one-to-one or one-to-many and whether zero records may skip the wizard step.

### Change login/access behavior

Trace all session keys through login, both notification views, both confirmation views, create, root routing, and logout. Test same-browser success, other-browser behavior, expired/tampered/replayed links, duplicate/mixed-case emails, email backend failures, and editing-disabled mode. Avoid logging access tokens or personal registration content.

### Fix authorization

Treat `participant_id` as untrusted session input. Resolve the participant, then scope every child query to that participant. Convert destructive routes to POST, include CSRF tokens, and test attempts to access another participant's primary keys. Consider consolidating this into a decorator/helper to prevent drift.

### Change conditional form behavior

Update both the template's `form-logic` JavaScript and server-side form/model validation. Test direct POSTs because clients can bypass hidden fields and JavaScript.

### Prepare deployment

Run `python manage.py check --deploy`, tests, migrations, and static collection in the actual environment. Externalize secrets, select config through explicit environment variables, configure HTTPS and secure cookies, validate allowed hosts/proxy headers, ensure log/data/media directories and backups, and remove or protect test/debug routes.

## 16. Suggested repair sequence

1. Add valid `max_length` values and establish migrations; restore a green `manage.py check` and test database creation.
2. Fix delete ownership and method semantics; add cross-participant security tests.
3. Externalize and rotate all committed secrets, then harden HTTPS/cookies/hosts.
4. Repair and test `OCIAParticipantSession.load_user_session()` paths; decide whether database sessions or Django sessions are authoritative.
5. Enforce normalized unique email identity and define duplicate-data migration behavior.
6. Add end-to-end tests for new and existing participant workflows and editing-disabled mode.
7. Remove unused imports/artifacts and document/install every runtime dependency.

## 17. Retrieval keywords

- **authentication / login / magic link / access code:** `OCIAParticipantLoginView`, notification/confirmation views, `OCIAParticipantView`, session keys.
- **authorization / IDOR / ownership / delete:** `OCIAParticipantDeleteRecordView`, update views, `participant_id`.
- **wizard / registration order / branching:** religion, engagement, marriage, parent, questions create views.
- **schema / participant data:** `apps/ocia_participant/models.py`, relationship overview above.
- **validation / fields / widgets:** `apps/ocia_participant/forms.py`, `main/form.html`, `base.html` FieldManager.
- **branding / colors / site icon:** `SiteSettings`, `lib.util.color_variant`, base template CSS variables.
- **email / SMTP / fake email:** settings email block and access notification views/templates.
- **editing lock:** `OCIAParticipantSettings.enable_editing`, `editing_disabled_error()`.
- **admin / exports / staff:** `apps/ocia_participant/admin.py` (no export feature is evident).
- **media:** `apps/maven`; independent from OCIA unless a requested feature explicitly connects them.
- **tests broken / migrations:** verification baseline and missing `max_length` fields.

## 18. AI maintenance rules

Before editing, inspect the exact source and `git diff`; preserve unrelated user changes. Do not assume the current test suite proves the workflow. For any participant-data endpoint, verify login, editing lock, object ownership, HTTP method, CSRF behavior, and redirect destination. Treat registration data as sensitive personal/religious information: avoid emitting it to logs or error pages. Never copy committed secret values into documentation, tests, chat, or new config. After changes, run the narrow tests first, then the full suite and `manage.py check`; if schema changed, inspect the generated migration.
