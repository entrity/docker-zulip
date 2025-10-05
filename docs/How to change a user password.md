# How to change a user password

## Opt 1: python shell
Open a python shell and use python to manually change a password.

```bash
# Enter docker container:
cd /var/www/zulip/duckofdoom/
docker-compose exec -u zulip zulip bash
# Within docker container:
/home/zulip/deployments/current/manage.py shell
```

```python
from zerver.models import UserProfile
user = UserProfile.objects.get(id=15)
from zerver.actions.user_settings import do_change_password
do_change_password(user, password='NC123changeme')
```

## Opt 2: trigger email from manage.py
https://zulip.readthedocs.io/en/latest/production/management-commands.html
```bash
# Within docker container:
/home/zulip/deployments/current/manage.py send_password_reset_email -u user@example.com
```