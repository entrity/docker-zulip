# How to create a user

In UI: [Organization settings > Users > Invitations]
Click 'Invite users to organization'

```sql
select id, email, full_name, api_key, uuid from zerver_userprofile;

-- Build a url to complete each signup process:
select email, concat('https://zulip.duckofdoom.com/accounts/do_confirm/', confirmation_key) from confirmation_confirmation cc join django_content_type ct on cc.content_type_id = ct.id join zerver_preregistrationuser pu on pu.id = cc.object_id where model = 'preregistrationuser';
```

## Mail setup
Set up postfix and opendkim.

## Test mail setup
echo "BODY" | mail -s "SUBJECT" "markim.ten@gmail.com"
