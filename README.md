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
- Deze installatie gebruikt **mkcert** voor lokale, vertrouwde TLS-certificaten (machine niet publiek bereikbaar). Voor productie op een publiek IP gebruik Let's Encrypt. 

---

## Prerequisites

- **Docker & Docker Compose v2** (`docker compose`)
- **Git**
- **mkcert** (voor lokale HTTPS)
- (Optioneel) **Docker Hub account** (voor Jenkins CI/CD)

---

## Snelstart — Eerste keer setup

### 1. Clone repository

```bash
git clone <repository-url>
cd doorlopende-projectopdracht-sergiuNE
```

---

### 2. Maak secrets aan

Maak de `secrets/` folder en vul wachtwoorden in: 

```bash
mkdir -p secrets

# Database root password
echo "your_secure_root_password" > secrets/db_root_password.txt

# Database user password
echo "your_secure_db_password" > secrets/db_password.txt

# LTI session secret (minimaal 32 chars)
openssl rand -base64 32 > secrets/session_secret.txt

# LTI OAuth secret
echo "lti_oauth_secret" > secrets/oauth_secret.txt
```

**⚠️ Belangrijk:** Deze files worden NIET gecommit naar git (zie `.gitignore`).

---

### 3. Genereer TLS certificaten met mkcert

**Installeer mkcert (Ubuntu/Debian):**

```bash
sudo apt update
sudo apt install libnss3-tools wget -y
wget "https://dl.filippo.io/mkcert/latest?for=linux/amd64" -O mkcert
chmod +x mkcert
sudo mv mkcert /usr/local/bin/
mkcert --version
```

**Maak lokale CA en certificaten:**

```bash
# Installeer lokale CA
mkcert -install

# Genereer certificaten (vervang 10.158.10.72 met jouw IP!)
mkdir -p certs
cd certs
mkcert -key-file moodle-key.pem -cert-file moodle-cert.pem 10.158.10.72 localhost moodle.local
cd ..
```

**Importeer root CA in je browser:**

```bash
# Vind CA locatie
mkcert -CAROOT

# Kopieer rootCA.pem naar je lokale machine
cp $(mkcert -CAROOT)/rootCA.pem ~/
```

Importeer in **Brave/Chrome (Windows)**: 
1. Open Certificate Manager (`certmgr.msc`) of via browser settings
2. Importeer `rootCA.pem` in **Trusted Root Certification Authorities**

Importeer in **Firefox**:
1. Settings → Privacy & Security → View Certificates → Authorities
2. Import `rootCA.pem` en vink "Trust this CA to identify websites" aan

**Herstart je browser!**

---

### 4. Start de stack

**Optie A: Teststack (snel LTI testen, zonder Traefik/Jenkins):**

```bash
docker compose -f ltitest.yaml up -d
```

**Optie B: Volledige productiestack:**

```bash
docker compose up -d
```

**Start monitoring stack (eerste keer)**

```bash
docker compose -f prometheus/docker-compose.monitoring.yml up -d
```

**Opmerking:** Deze stap is alleen nodig bij de eerste setup. Monitoring containers blijven daarna draaien door restart: unless-stopped.

**Wacht ~2 minuten** voor alle services opstarten.

---

### 5. Verifieer dat alles draait

```bash
docker ps
```

Je moet zien:  `moodle`, `mariadb`, `ltitool`, `traefik`, `jenkins`, `prometheus`, `grafana`, `cadvisor`, `node-exporter`

---

### 6. Toegang tot services

| Service | URL | Opmerking |
|---------|-----|-----------|
| **Moodle** | https://10.158.10.72/ |
| **LTI Tool** | https://10.158.10.72/lti | Toont GET "LTI Tool is running! This endpoint expects a POST request from Moodle LTI." De LTI opent u vanuit Moodle intern, maar de LTI is ook beschikbaar via deze URL.
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

**Moodle login:**
- Regular user: `user` / `bitnami`

**Grafana login:**
- Default: `admin` / `admin` (wijzig bij eerste login)

---

## Jenkins CI/CD Setup

### 1. Unlock Jenkins

Eerste keer opstarten:  haal admin wachtwoord op: 

```bash
docker compose logs jenkins | grep -A 5 "password"
# OF
docker compose exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

Login op http://10.158.10.72/jenkins met dit wachtwoord.

---

### 2. Installeer suggested plugins

Kies **"Install suggested plugins"** tijdens setup wizard.

---

### 3. Configureer Docker Hub credentials

Voor automatische push naar Docker Hub:

1. **Jenkins** → **Manage Jenkins** → **Credentials** → **System** → **Global credentials**
2. **Add Credentials**:
   - Kind: `Username with password`
   - Username: `<jouw-dockerhub-username>`
   - Password: `<jouw-dockerhub-password>`
   - ID: `dockerhub-credentials`
3. **Save**

**⚠️ Belangrijk:** De `Jenkinsfile` verwacht credential ID `dockerhub-credentials`.

---

### 4. Configureer Jenkins agent (optioneel)

Voor gebruik van externe build agent:

1. Genereer SSH keypair:
   ```bash
   ssh-keygen -t ed25519 -f jenkins-key
   ```

2. Op target machine:
   ```bash
   sudo apt install openjdk-17-jre
   sudo useradd -m -s /bin/bash jenkins
   sudo mkdir -p /home/jenkins/.ssh
   sudo nano /home/jenkins/.ssh/authorized_keys  # Plak public key
   sudo chown -R jenkins:jenkins /home/jenkins/.ssh
   sudo chmod 700 /home/jenkins/.ssh
   sudo chmod 600 /home/jenkins/.ssh/authorized_keys
   ```

3. In Jenkins GUI:
   - **Manage Jenkins** → **Credentials** → Add private key (ID: `jenkins-ssh-key`)
   - **Manage Jenkins** → **Nodes** → **New Node** (label: `bletchley`)

---

### 5. Pipeline setup

De pipeline draait automatisch bij git push via de `Jenkinsfile`.

**Stages:**
1. **Build** - Bouwt LTI Docker image
2. **Push** - Pusht naar Docker Hub (vereist credentials!)
3. **Deploy** - Herstart stack met `docker compose up -d --build`

---

## LTI Tool configuratie in Moodle

### 1. Login als admin

`admin` / `bitnami`

---

### 2. Voeg External Tool toe

1. **Site administration** (⚙️) → **Plugins** → **Activity modules** → **External tool** → **Manage tools**
2. **Configure a tool manually**:
   - Tool name: `Test LTI Tool`
   - Tool URL: `https://10.158.10.72/lti`
   - Consumer key: `test_key` (vrij te kiezen)
   - Shared secret: `lti_oauth_secret` (moet matchen met `secrets/oauth_secret.txt`)
   - Tool configuration usage: **Show as preconfigured tool**
3. **Save changes**

---

### 3. Voeg tool toe aan cursus

1. Ga naar **Test Course**
2. **Turn editing on**
3. **Add an activity** → **External tool**
4. Selecteer je geconfigureerde tool
5. **Save and display**

---

## Monitoring

**Prometheus targets:** http://10.158.10.72:9090/targets  
**Grafana dashboards:** http://10.158.10.72:3000/dashboard  
**Traefik Metrics:** http://10.158.10.72:8081/metrics   
**Prometheus Metrics:** http://10.158.10.72:9090/metrics  
**Node Exporter:** http://10.158.10.72:9100/metrics   
**cAdvisor Metrics:** http://10.158.10.72:8082/metrics 

**Pre-configured dashboards:**
- Traefik metrics (request rates, latency)
- System metrics (CPU, RAM, disk via Node Exporter)
- Container metrics (cAdvisor)

**Prometheus quick start:**
- Ga naar **Status** → **Targets** om health te controleren
- Type in query bar: `up` om alle targets te zien
- Type in query bar: `container_memory_usage_bytes` om container metrics te zien

**Grafana quick start:**
- Login:  `admin` / `admin` (verander wachtwoord bij eerste login)
- Ga naar **Dashboards** om pre-configured dashboards te zien
- Klik **Import** om extra dashboards toe te voegen

---

## Project structuur

```
. 
├── docker-compose.yaml                      # Productie stack
├── ltitest.yaml                             # Test stack
├── traefik-config.yml                       # Traefik TLS config
├── Jenkinsfile                              # CI/CD pipeline
├── prometheus.yml                           # Prometheus configuratie
├── certs/                                   # mkcert certificaten (niet in git)
│   ├── moodle-cert.pem
│   └── moodle-key.pem
├── secrets/                                 # Wachtwoorden (niet in git)
│   ├── db_password.txt
│   ├── db_root_password.txt
│   ├── oauth_secret.txt
│   └── session_secret.txt
├── ltitool/                                 # LTI applicatie source
│   ├── static/
|   |   ├── roadmapstyle.css
│   ├── Dockerfile
│   ├── ltitool.py
│   ├── README.md
│   └── requirements.txt
├── prometheus/                              # Prometheus monitoring stack
│   └── docker-compose.monitoring.yml
├── traefik/                                 # Traefik configuratie
│   ├── dynamic.yml
│   └── traefik.yml
├── PROGRESS.md                              # Projectvoortgang
├── versions.md                              # Changelog
├── .gitignore                               # Git ignore rules
└── README.md                                # Deze file
```

---

## Architectuur

### Netwerken

**Frontend** (`frontend`):
- Traefik, Moodle, LTI tool, Jenkins, Prometheus, Grafana & cAdvisor
- Toegankelijk vanaf host machine

**Backend** (`backend`):
- MariaDB (internal network, geen internet access)
- Alleen Moodle kan erbij

### Security

- **Docker secrets** voor gevoelige data (niet in environment variables)
- **Network isolation** (database niet publiek bereikbaar)


---

## Referenties

- **Moodle documentatie**: https://docs.moodle.org/
- **Traefik docs**: https://doc.traefik.io/traefik/
- **mkcert**: https://github.com/FiloSottile/mkcert

---

**Versie**:  Zie `versions.md` voor changelog  
**Voortgang**:  Zie `PROGRESS.md` voor gedetailleerde projectstatus  
**Auteur**: Neagu Sergiu