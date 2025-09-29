# How to change a user password

Open a python shell and use python to manually change a password.

```bash
./manage.py shell
```

```python
from zerver.models import UserProfile
user = User.objects.get(id=15)
from zerver.actions.user_settings import do_change_password
do_change_password(user, password='NC123changeme')
```