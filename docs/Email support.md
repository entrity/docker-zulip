# Email support

## Set up on host

Install postfix and opendkim on the host. Postfix will be running in chroot jail, so in `/etc/postfix/main.cf` and `/etc/opendkim.conf`, set up the socket to be the same thing but in a place accessible from the jail:

```
# /etc/postfix/main.cf
smtpd_milters = unix:/opendkim/opendkim.sock
# /etc/opendkim.conf
Socket			local:/var/spool/postfix/opendkim/opendkim.sock
```

## Set up DNS

On registrar (namecheap.com), set up txt records for DKIM, DMARC, SPF.

On vm service (stallion), set up PTR.

## Config in zulip

Update docker-compose to specify:
```yaml
SETTING_EMAIL_HOST: "172.18.0.1"
SETTING_EMAIL_HOST_USER: ""
SETTING_EMAIL_HOST_PASSWORD: ""
SETTING_EMAIL_PORT: "25"
SETTING_EMAIL_BACKEND: "django.core.mail.backends.smtp.EmailBackend"
SETTING_EMAIL_FROM: "Zulip <...@...>"
SETTING_FROM_EMAIL: "Zulip <...@...>"
```
...where `SETTING_EMAIL_HOST` is the host's ip address on the docker network. (I got it by running `ip a | grep 172.18.0.` because I knew that the subnet for my zulip network was `172.18.0.0/24`, thanks to `docker network inspect zulip_default`.)

...and of `SETTING_EMAIL_FROM` and `SETTING_FROM_EMAIL`, surely only one is needed, and I didn't really use `...@...`; I used `noreply@DOMAIN.COM`.

...and I don't think `SETTING_EMAIL_BACKEND` or `SETTING_EMAIL_HOST_PASSWORD` are needed.

...and maybe installing ssmtp in the container was important too. After doing so, I `docker commit ...` to save my changes to the image.
