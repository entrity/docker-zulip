## The problem

3 cron jobs were scheduled for the same time. They eat up all the memory, which leads to thrashing (swapping), which eats all of the CPU.

## The solution

Replace 3 files in `/etc/cron.d` with a single file which runs the three tasks in parallel.

```bash
# On the host
docker exec -it -u zulip zulip_zulip_1 bash
# In the container
cat <<-EOF > ~zulip/sequential-cron-tasks-5am.sh
#!/bin/bash

# sequential-cron-tasks-5am.sh

# Run 3 tasks which used to be in /etc/cron.d. I moved them out because they
# were scheduled for the same time and when they ran, it depleted the
# machine's memory.

cd /home/zulip/deployments/current/ && ./manage.py delete_old_unclaimed_attachments -f >/dev/null

cd /home/zulip/deployments/current/ && ./manage.py soft_deactivate_users -d >/dev/null

# This one is really only supposed to run on Sundays
cd /home/zulip/deployments/current/ && ./manage.py update_channel_recently_active_status >/dev/null
EOF
chown zulip:zulip ~zulip/sequential-cron-tasks-5am.sh
cat <<-EOF > /etc/cron.d/sequential-tasks-to-save-memory-5am
MAILTO=zulip
PATH=/usr/local/bin:/usr/bin:/bin
SHELL=/bin/bash
USER=zulip
RUNNING_UNDER_CRON=1
HTTP_proxy="http://localhost:4750"
HTTPS_proxy="http://localhost:4750"

0 5 * * *    zulip    cd /home/zulip/ && bash sequential-cron-tasks-5am.sh
EOF
rm /etc/cron.d/update-channel-recently-active-status /etc/cron.d/delete-old-unclaimed-attachments /etc/cron.d/soft-deactivate-users
```

## Journal

I found that the CPU was being eaten up and taking down all services every so often.

I downloaded an atop log form `/var/log/atop` and reviewed it on my laptop (moving it from eastern time to pacific time): `atop -r atop_20250921 -b 21:57 -e 22:04 -l`. That gave 3 snapshots: smooth sailing, low available memory, very low available memory.

It was these processes that showed up in the 2nd and 3rd snapshots which made the difference:
```
44093       - D   7% python3 ./manage.py update_channel_recently_active_status
44094       - D   7% python3 ./manage.py delete_old_unclaimed_attachments -f
44095       - D   7% python3 ./manage.py soft_deactivate_users -d
```

And looking at the first of those processes, I see its ancestors are:
```bash
/bin/bash -c    cd /home/zulip/deployments/current/ && ./manage.py update_channel_recently_active_status >/dev/null
/usr/sbin/CRON -f -L 15
/usr/sbin/cron -f -L 15
/usr/bin/python3 /usr/bin/supervisord -n -c /etc/supervisor/supervisord.conf
# After that, it appears to go to the docker service itself: containerd-shim
```
These processes are in the cgroup `/system.slice/docker-ed77d1877cdfd7c9272a5ba9d25043933365e80d41`, which is a giveaway that it's running in a docker container. The cgroup's name suggests it's probably the container whose id is `ed77d1877cdf`, which runs the zulip application, which is where I expected to find these processes in the first place.

Within the container, I found where thse processes were scheduled:
```bash
grep -rP '^\d+ 5' /etc/cron.*
# => /etc/cron.d/update-channel-recently-active-status:
# =>     0 5 * * 0    zulip    cd /home/zulip/deployments/current/ && ./manage.py update_channel_recently_active_status >/dev/null
# => /etc/cron.d/delete-old-unclaimed-attachments:
# =>     0 5 * * *    zulip    cd /home/zulip/deployments/current/ && ./manage.py delete_old_unclaimed_attachments -f >/dev/null
# => /etc/cron.d/soft-deactivate-users:
# =>     0 5 * * *    zulip    cd /home/zulip/deployments/current/ && ./manage.py soft_deactivate_users -d >/dev/null
```

The timing looks correct because the container is running on UTC. (UTC 5 - 7 = Pacific 10 pm. And the memory issue shows up at about 22:00 Pacific when I download and review the `atop` log file on my laptop.)

So I rewrote the crontab to do these 3 jobs in a series instead of in parallel.

_update 2025-10-05_

I found the same issue happened again at the same time a week later. Makes me think the Sunday task is the big problem. But why didn't my fix persist? All the three old cron files were right back in their places, alongside my new one. I deleted them anew, then committed the update: `docker commit zulip_zulip_1 zulip/docker-zulip:11.0-0`