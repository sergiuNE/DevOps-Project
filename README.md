# Doorlopende Projectopdracht — Moodle 4.4 met LTI, Traefik, Jenkins & Monitoring

## Beschrijving

Deze repository bevat een Docker Compose based deployment van:
- **Moodle 4.4** (Bitnami legacy image)
- **MariaDB** (persistente opslag)
- **LTI-tool** (externe applicatie geïntegreerd in Moodle)
- **Traefik** als reverse-proxy / TLS terminator
- **CI/CD via Jenkins** (build, push, redeploy)
- **Monitoring**: Prometheus, Grafana, cAdvisor, Node Exporter

**Doel**: een reproduceerbare dev / productiesetup waarbij: 
- `ltitest.yaml` = teststack (zonder Traefik & Jenkins) om LTI snel te testen
- `docker-compose.yaml` = productiestack (Traefik, secrets, netwerken, monitoring, Jenkins)

---

## Belangrijk

- **Gebruik geen plaintext credentials in git. ** Gevoelige waarden zitten in `./secrets/` en worden als Docker secrets gebruikt.
- **Bitnami legacy images** worden gebruikt zoals vereist door de opdracht.
- Deze installatie gebruikt **mkcert** voor lokale, vertrouwde TLS-certificaten (machine niet publiek bereikbaar). Voor productie op een publiek IP gebruik Let's Encrypt op een domein.

---

## Prerequisites

- Docker & Docker Compose v2 (`docker compose`)
- Git
- mkcert (voor lokale HTTPS, zie sectie)
- (Optioneel) toegang tot een cloud VPS (Hetzner) voor publicatie

---

## Project structuur (belangrijkste items)

```
. 
├── docker-compose.yaml          # productiestack (Traefik, Moodle, LTI, Jenkins, monitoring)
├── ltitest.yaml                 # teststack (Moodle + LTI zonder Traefik/Jenkins)
├── traefik-config.yml           # Traefik dynamic TLS config
├── certs/                       # mkcert gegenereerde cert/key
├── secrets/                     # Docker secret files 
├── Jenkinsfile                  # pipeline config voor build/push/deploy
├── PROGRESS.md                  # voortgangsnotities
├── versions.md                  # versie changelog
├── ltitool/                     # LTI applicatie source
├── traefik/                     # Traefik configuratie
├── prometheus/                  # Prometheus config
└── jenkins/                     # Jenkins setup docs
```

---

## Toegang — Test setup

*(IP VM: `10.158.10.72`)*

| Service | URL |
|---------|-----|
| **Moodle** | https://10.158.10.72/ |
| **LTI Tool** | https://10.158.10.72/lti |
| **LTI Health** | https://10.158.10.72/lti/health |
| **Traefik Dashboard** | http://10.158.10.72:8081/dashboard/ |
| **Traefik Metrics** | http://10.158.10.72:8081/metrics |
| **Prometheus** | http://10.158.10.72:9090 |
| **Prometheus Metrics** | http://10.158.10.72:9090/metrics |
| **Grafana** | http://10.158.10.72:3000 |
| **Node Exporter** | http://10.158.10.72:9100/metrics |
| **cAdvisor** | http://10.158.10.72:8082 |
| **cAdvisor Metrics** | http://10.158.10.72:8082/metrics |
| **Jenkins** | http://10.158.10.72/jenkins |

**Default Moodle login**: `user` / `bitnami`

---

## Snel starten (ontwikkel / test)

### 1) Teststack (zonder Traefik / Jenkins) — snel LTI testen

```bash
# vanuit repo root
docker compose -f ltitest.yaml up -d
```

**Stop / herstart:**
```bash
docker compose -f ltitest.yaml down
docker compose -f ltitest.yaml up -d
```

---

### 2) Productiestack (Traefik, TLS, Jenkins, monitoring)

```bash
# start alle services defined in docker-compose.yaml
docker compose up -d
```

**Stop / herstart:**
```bash
docker compose down
docker compose up -d
```

---

## mkcert — korte handleiding (lokale TLS)

### 1. Installeer mkcert op je machine

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install libnss3-tools wget -y
wget "https://dl.filippo.io/mkcert/latest?for=linux/amd64" -O mkcert
chmod +x mkcert
sudo mv mkcert /usr/local/bin/
mkcert --version
```

### 2. Maak en installeer een lokale CA

```bash
mkcert -install
```

### 3. Genereer certificates

```bash
mkdir -p certs
cd certs
mkcert -key-file moodle-key.pem -cert-file moodle-cert.pem 10.158.10.72 localhost moodle.local
```

De gegenereerde bestanden `moodle-cert.pem` en `moodle-key.pem` moeten in `./certs/` staan zodat Traefik ze kan mounten. 

### 4. Importeer rootCA in je browser

Zie volgende sectie! 

---

## Root CA importeren (voor browsers)

### Exporteer rootCA.pem

```bash
mkcert -CAROOT   # toont directory, bv ~/. local/share/mkcert
cp $(mkcert -CAROOT)/rootCA.pem ~/
```

### Kopieer naar je lokale machine

Gebruik SCP / HTTP server / USB om `rootCA.pem` naar je Windows/Mac machine te krijgen.

### Importeer in browser

**Brave/Chrome (Windows):**
1. Open Certificate Manager (certmgr.msc of via browser settings)
2. Importeer `rootCA.pem` in **"Trusted Root Certification Authorities"**

**Firefox:**
1. Preferences → Privacy & Security → View Certificates
2. Authorities → Import
3. Vink **"Trust this CA to identify websites"** aan

**Herstart browser! **

---

## Traefik TLS (hoe het werkt hier)

- `traefik-config.yml` wordt door Traefik als dynamische provider geladen (gemount in container)
- `certs/` map bevat `moodle-cert.pem` + `moodle-key.pem` en wordt gemount op `/etc/traefik/certs`
- Traefik gebruikt het als default TLS cert 
- HTTP → HTTPS redirect via `redirect-to-https` middleware (standaard aanwezig in labels)

---

## Secrets & veiligheid

- Configureer wachtwoorden in `./secrets/` (lokale files)
- Wachtwoordbestanden moeten **NIET** naar git gepusht worden
- Voor productie in de cloud (Hetzner) gebruik cloud provider secrets of environment vaults

**Secrets in deze setup:**
- `db_root_password.txt` - MariaDB root password
- `db_password.txt` - Moodle database password
- `session_secret.txt` - LTI session secret
- `oauth_secret.txt` - LTI OAuth secret

---

## Jenkins / CI-CD

- Pipeline is beschreven in `Jenkinsfile`
- Jenkins bouwt images, pusht naar Docker Hub en runt deploy stage
- **Toegang**: http://10.158.10.72/jenkins

**Admin wachtwoord ophalen:**
```bash
docker compose logs jenkins | grep -A 5 "password"
# OF
docker compose exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

**Pipeline flow:**
1. **Build** - Bouwt LTI Docker image
2. **Push** - Pusht naar Docker Hub
3. **Deploy** - Herstart Moodle stack met nieuwe images

---

### Jenkins Agent Setup

Voor gebruik van een externe agent (bijv. Bletchley machine):

1. **SSH configuratie:** voeg jenkins user toe in `/etc/ssh/sshd_config`
2. **Maak keypair:** 
   ```bash
   ssh-keygen -t ed25519 -f jenkins-key
   ```
3. **Installeer Java:** 
   ```bash
   sudo apt install openjdk-17-jre
   ```
4. **Maak jenkins user:** 
   ```bash
   sudo useradd -m -s /bin/bash jenkins
   ```
5. **Voeg public key toe** aan `/home/jenkins/.ssh/authorized_keys`
6. **Voeg private key toe** in Jenkins Credentials (ID: `jenkins-ssh-key`)
7. **Voeg agent toe** in Jenkins GUI (label: `bletchley`)


## Monitoring

- **Prometheus** scrapes metrics van Traefik, cAdvisor, Node Exporter
- **Grafana** dashboards voor visualisatie (Traefik, Node Exporter, system metrics)
- **Check targets**: http://10.158.10.72:9090/targets

**Grafana default login**:  `admin` / `admin` (verandert na eerste login)

**Dashboards:**
- Traefik metrics
- System metrics (Node Exporter)
- Container metrics (cAdvisor)

---


**Versie**:  Zie `versions.md` voor changelog  
**Voortgang**: Zie `PROGRESS.md` voor gedetailleerde projectstatus


*Gemaakt door*: Neagu Sergiu 