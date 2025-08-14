Set up config for apache according to doc. (see below)
I started out by just setting it up for port 80.
Then I ran `sudo certbot` to install certs.
Then I updated the generated file for port 443 according to the doc:
https://zulip.readthedocs.io/en/latest/production/reverse-proxies.html#apache2-configuration

Get docker-compose.yml from the repo
https://github.com/zulip/docker-zulip?tab=readme-ov-file
Update it according to instructions in the repo's README.
Also update it to prevent to the host. I'll have my server do a gateway to this container.

```bash
docker-compose pull
docker-compose up -d


docker-compose exec -u zulip zulip cat ~zulip/deployments/current/puppet/zulip/files/nginx/dhparam.pem | sudo tee /etc/apache2/zulip-nginx/dhparam.pem

# Don't do any of the following. Just rely on the docker-compose file

HOST_IP=$(curl ifconfig.me)
echo -e "\n[loadbalancer]\nips = $HOST_IP" | docker-compose exec -u zulip -T zulip tee -a /etc/zulip/zulip.conf
docker-compose exec -u zulip zulip cat /etc/zulip/zulip.conf
/home/zulip/deployments/current/scripts/zulip-puppet-apply
# /home/zulip/deployments/current/scripts/restart-server
# Prev cmd doesn't work. Restart docker containers


echo -e "\n[application_server]\nhttp_only = true" | docker-compose exec -u zulip -T zulip tee -a /etc/zulip/zulip.conf
docker-compose exec -u zulip zulip cat /etc/zulip/zulip.conf
# /home/zulip/deployments/current/scripts/restart-server
# Prev cmd doesn't work. Restart docker containers


docker-compose exec -u zulip zulip /home/zulip/deployments/current/manage.py generate_realm_creation_link
# Click the link, generate an organization
```

## Troubleshooting
**`503`**
Have to restart apache after changing container's ip address in /etc/hosts


**`ERROR: for zulip  'ContainerConfig'**
```bash
docker-compose down
# docker system prune --volumes
# docker-compose up
# docker rmi -f zulip/docker-zulip:10.4-0
# docker-compose up
# docker image prune -a # This will delete all images that don't have a container currently running
# docker-compose up
# docker system prune
# docker-compose up
```

**403 when creating a new organization**
