# Jenkins Setup

## Admin Wachtwoord Ophalen

```bash
docker compose logs jenkins | grep -A 5 "password"
```

Of:

```bash
docker compose exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

## Toegang

- Jenkins: http://10.158.10. 72/jenkins
- Traefik Dashboard: http://10.158.10.72:8081

## Agent Setup 
1. **SSH configuratie:** voeg jenkins user toe in `/etc/ssh/sshd_config`
2. **Maak keypair:** `ssh-keygen -t ed25519 -f jenkins-key`
3. **Installeer Java:** `sudo apt install openjdk-17-jre`
4. **Maak jenkins user:** `sudo useradd -m -s /bin/bash jenkins`
5. **Voeg public key toe** aan `/home/jenkins/.ssh/authorized_keys`
6. **Voeg private key toe** in Jenkins Credentials (ID: `jenkins-ssh-key`)
7. **Voeg agent toe** in Jenkins GUI (label: `bletchley`)

## Pipeline

Pipeline draait uit `Jenkinsfile` in repo root.  Bouwt LTI image en deployt stack.

**Let op:** Geen private keys in deze map committen! 