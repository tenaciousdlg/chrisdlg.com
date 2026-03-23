---
title: "Breaking Your Blog, Via Your Database"
date: 2022-01-15
description: "How a new laptop and mismatched database passwords brought down my Ghost blog — and what it took to recover it from a Docker container."
tags: [docker, mariadb, ghost, debugging]
draft: true
---

I recently switched to a new computer. As part of that process I started setting up my personal development environment and downloaded the [repo](https://github.com/delag/tf-blog) that powers this [an old] blog.

After downloading the repo I made a copy of the `terraform.tfvars.example` file to `terraform.tfvars` in the same directory. I then updated the variables, not thinking twice about it (hint, hint), and proceeded to run `terraform init && terraform apply --auto-approve` to get the directory and the blog back up and running.

> It should be noted that I had run `terraform destroy` before getting rid of my previous development environment. The commands ran above were intended to bring the blog back online, which at the time was offline.

Terraform did its job and brought my infrastructure back up. However, when I went to try and visit this blog I was getting a 503 error. A HTTP 503 means the service is unavailable. I usually treat this like a HTTP 502 (Bad Gateway) in a setup like this — think of it as layers. There is the Terraform config, which creates the VM, which then populates services and configures them, then there is the Docker stack and the application containers depending on a few things. The first step is trying to draw some logical conclusions and see where I could eliminate possibilities.

I first tried logging into my DigitalOcean (DO) droplet but found it didn't like my SSH key. After re-creating my SSH key, uploading it to DO, and referencing the new key in my `terraform.tfvars` file I was able to get into the machine.

Running `docker ps` showed that the containers had created but the ghost container was in a restart loop due to a failure. Anytime you run into something like this, `docker logs <containerID or name>` is your friend. You can even run `docker logs -f <containerID or name>` to follow the container's logs in real time.

The ghost container's logs indicated it was receiving a permission denied message from the MariaDB container. I then checked the MariaDB container's logs and saw the same thing.

```
2021-12-22 21:36:44 3 [Warning] Access denied for user 'ghostuser'@'172.x.x.x' (using password: YES)
```

My first thought was that I messed up something in the `terraform.tfvars` file, but Terraform should have caught that. In other words, if I did not set a variable correctly then `terraform apply` should have detected it.

Next was to check on the MariaDB container's environment variables and then try to use those variables to log in to the database itself. Running `docker exec <containerID or name> env` showed me that the environment variables matched what I had provided in the `terraform.tfvars` file. A quick review of the `docker-compose.yml` file at `/opt/scripts` on the DO droplet confirmed they were written correctly as well.

Logging into the MariaDB container via `docker exec -it <containerID or name> /bin/bash` allowed me to try logging into the database. The way to do that for a MariaDB (MySQL) database is to run `mysql -u root -p`.

> I am using the root MariaDB user due to my setup. The user you use can differ, and this is not best practice.

You can also use `mysql --user=root --password=password` but this leaves your password in your command line history and should be avoided.

After tailing the logs to confirm what I was seeing, I found I could not log in as the `root` or `ghostuser` database users from the container's command line. This did not make any sense. The container was new, I set the passwords — they should be working!?! Whenever I run into a problem like that I find it best to walk away for a bit.

While walking, it dawned on me that the MariaDB databases, users, and data weren't ephemeral. They were being mounted from the Cloud Block Storage that persisted outside of my Terraform config. This meant that the random passwords I chose for the MariaDB `root` and `ghostuser` on my new workstation did not match what was *already* on the persistent cloud block storage.

Now that I had identified the problem it was time to work on a solution. The problem statement was: "how to update the `root` database user's password on a container." In normal MySQL/MariaDB land — running it as a service on a machine — you would stop the database service and bring it back up while skipping privilege checks (i.e. password requirements for database users).

> Skipping privileges for database users is inherently dangerous as it leaves your database open to attack. If you need to do this, do so in a maintenance window when networking to the database is restricted — or if that isn't available, as quickly as possible.

The folks over at DO have a [great article](https://www.digitalocean.com/community/tutorials/how-to-reset-your-mysql-or-mariadb-root-password-on-ubuntu-20-04) on how to reset the password for the MariaDB `root` user. That didn't address how to do it on a container. The container is just a packaged version of the MariaDB service running on a slimmed-down OS — there is no `systemctl` to manage the database service. Everything needs to be done through container orchestration.

<!-- TODO: finish this — describe how you resolved it via docker-compose override or init flags to skip-grant-tables, then restored normal operation -->
