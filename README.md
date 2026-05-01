# Ongoing Project Assignment — Moodle 4.4 with LTI, Traefik, Jenkins & Monitoring

## Description

This repository contains a Docker Compose based deployment of:

- **Moodle 4.4** (Bitnami legacy image)
- **MariaDB** (persistent storage)
- **LTI tool** (external application integrated in Moodle)
- **Traefik** as reverse proxy / TLS terminator
- **CI/CD via Jenkins** (build, push, redeploy)
- **Monitoring**: Prometheus, Grafana, cAdvisor, Node Exporter

**Goal**: a reproducible dev / production setup where:
- `ltitest.yaml` = test stack (without Traefik & Jenkins) for quickly testing LTI
- `docker-compose.yaml` = production stack (Traefik, secrets, networks, monitoring, Jenkins)

---

## Important

- **Do not use plaintext credentials in git.** Sensitive values are stored in `./secrets/` and used as Docker secrets.
- **Bitnami legacy images** are used as required by the assignment.
- This installation uses **mkcert** for local, trusted TLS certificates (machine not publicly reachable). For production on a public IP, use Let's Encrypt.

---

## Prerequisites

- **Docker & Docker Compose v2** (`docker compose`)
- **Git**
- **mkcert** (for local HTTPS)
- (Optional) **Docker Hub account** (for Jenkins CI/CD)

---

## Quick Start — First-time Setup

### 1. Clone repository

```bash
git clone <repository-url>
cd doorlopende-projectopdracht-sergiuNE
```

---

### 2. Create secrets

Create the `secrets/` folder and fill in passwords:

```bash
mkdir -p secrets

# Database root password
echo "your_secure_root_password" > secrets/db_root_password.txt

# Database user password
echo "your_secure_db_password" > secrets/db_password.txt

# LTI session secret (minimum 32 chars)
openssl rand -base64 32 > secrets/session_secret.txt

# LTI OAuth secret
echo "lti_oauth_secret" > secrets/oauth_secret.txt
```

**⚠️ Important:** These files are NOT committed to git (see `.gitignore`).

---

### 3. Generate TLS certificates with mkcert

**Install mkcert (Ubuntu/Debian):**

```bash
sudo apt update
sudo apt install libnss3-tools wget -y
wget "https://dl.filippo.io/mkcert/latest?for=linux/amd64" -O mkcert
chmod +x mkcert
sudo mv mkcert /usr/local/bin/
mkcert --version
```

**Create local CA and certificates:**

```bash
# Install local CA
mkcert -install

# Generate certificates (replace 10.158.10.72 with your IP!)
mkdir -p certs
cd certs
mkcert -key-file moodle-key.pem -cert-file moodle-cert.pem 10.158.10.72 localhost moodle.local
cd ..
```

**Import root CA into your browser:**

```bash
# Find CA location
mkcert -CAROOT

# Copy rootCA.pem to your local machine
cp $(mkcert -CAROOT)/rootCA.pem ~/
```

Import in **Brave/Chrome (Windows)**:
1. Open Certificate Manager (`certmgr.msc`) or via browser settings
2. Import `rootCA.pem` into **Trusted Root Certification Authorities**

Import in **Firefox**:
1. Settings → Privacy & Security → View Certificates → Authorities
2. Import `rootCA.pem` and check "Trust this CA to identify websites"

**Restart your browser!**

---

### 4. Start the stack

**Option A: Test stack (quick LTI testing, without Traefik/Jenkins):**

```bash
docker compose -f ltitest.yaml up -d
```

**Option B: Full production stack:**

```bash
docker compose up -d
```

**Start monitoring stack (first time)**

```bash
docker compose -f prometheus/docker-compose.monitoring.yml up -d
```

**Note:** This step is only required during the first setup. Monitoring containers will continue running afterwards due to `restart: unless-stopped`.

**Wait ~2 minutes** for all services to start up.

---

### 5. Verify everything is running

```bash
docker ps
```

You should see: `moodle`, `mariadb`, `ltitool`, `traefik`, `jenkins`, `prometheus`, `grafana`, `cadvisor`, `node-exporter`

---

### 6. Access to services

| Service | URL | Notes |
|---------|-----|-------|
| **Moodle** | https://10.158.10.72/ |
| **LTI Tool** | https://10.158.10.72/lti | Shows GET "LTI Tool is running! This endpoint expects a POST request from Moodle LTI." The LTI is opened from within Moodle, but the LTI is also accessible via this URL.
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
- Default: `admin` / `admin` (change on first login)

---

## Jenkins CI/CD Setup

### 1. Unlock Jenkins

First startup: retrieve the admin password:

```bash
docker compose logs jenkins | grep -A 5 "password"
# OR
docker compose exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

Login at http://10.158.10.72/jenkins with this password.

---

### 2. Install suggested plugins

Choose **"Install suggested plugins"** during the setup wizard.

---

### 3. Configure Docker Hub credentials

For automatic push to Docker Hub:

1. **Jenkins** → **Manage Jenkins** → **Credentials** → **System** → **Global credentials**
2. **Add Credentials**:
   - Kind: `Username with password`
   - Username: `<your-dockerhub-username>`
   - Password: `<your-dockerhub-password>`
   - ID: `dockerhub-credentials`
3. **Save**

**⚠️ Important:** The `Jenkinsfile` expects credential ID `dockerhub-credentials`.

---

### 4. Configure Jenkins agent (optional)

For use of an external build agent:

1. Generate SSH keypair:
   ```bash
   ssh-keygen -t ed25519 -f jenkins-key
   ```

2. On target machine:
   ```bash
   sudo apt install openjdk-17-jre
   sudo useradd -m -s /bin/bash jenkins
   sudo mkdir -p /home/jenkins/.ssh
   sudo nano /home/jenkins/.ssh/authorized_keys  # Paste public key
   sudo chown -R jenkins:jenkins /home/jenkins/.ssh
   sudo chmod 700 /home/jenkins/.ssh
   sudo chmod 600 /home/jenkins/.ssh/authorized_keys
   ```

3. In Jenkins GUI:
   - **Manage Jenkins** → **Credentials** → Add private key (ID: `jenkins-ssh-key`)
   - **Manage Jenkins** → **Nodes** → **New Node** (label: `bletchley`)

---

### 5. Pipeline setup

The pipeline runs automatically on git push via the `Jenkinsfile`.

**Stages:**
1. **Build** - Builds the LTI Docker image
2. **Push** - Pushes to Docker Hub (requires credentials!)
3. **Deploy** - Restarts stack with `docker compose up -d --build`

---

## LTI Tool configuration in Moodle

### 1. Login as admin

`admin` / `bitnami`

---

### 2. Add External Tool

1. **Site administration** (⚙️) → **Plugins** → **Activity modules** → **External tool** → **Manage tools**
2. **Configure a tool manually**:
   - Tool name: `Test LTI Tool`
   - Tool URL: `https://10.158.10.72/lti`
   - Consumer key: `test_key` (freely chosen)
   - Shared secret: `lti_oauth_secret` (must match `secrets/oauth_secret.txt`)
   - Tool configuration usage: **Show as preconfigured tool**
3. **Save changes**

---

### 3. Add tool to course

1. Go to **Test Course**
2. **Turn editing on**
3. **Add an activity** → **External tool**
4. Select your configured tool
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
- Go to **Status** → **Targets** to check health
- Type in the query bar: `up` to see all targets
- Type in the query bar: `container_memory_usage_bytes` to see container metrics

**Grafana quick start:**
- Login: `admin` / `admin` (change password on first login)
- Go to **Dashboards** to see pre-configured dashboards
- Click **Import** to add extra dashboards

---

## Project structure

```
.
├── docker-compose.yaml                      # Production stack
├── ltitest.yaml                             # Test stack
├── traefik-config.yml                       # Traefik TLS config
├── Jenkinsfile                              # CI/CD pipeline
├── prometheus.yml                           # Prometheus configuration
├── certs/                                   # mkcert certificates (not in git)
│   ├── moodle-cert.pem
│   └── moodle-key.pem
├── secrets/                                 # Passwords (not in git)
│   ├── db_password.txt
│   ├── db_root_password.txt
│   ├── oauth_secret.txt
│   └── session_secret.txt
├── ltitool/                                 # LTI application source
│   ├── static/
|   |   ├── roadmapstyle.css
│   ├── Dockerfile
│   ├── ltitool.py
│   ├── README.md
│   └── requirements.txt
├── prometheus/                              # Prometheus monitoring stack
│   └── docker-compose.monitoring.yml
├── traefik/                                 # Traefik configuration
│   ├── dynamic.yml
│   └── traefik.yml
├── PROGRESS.md                              # Project progress
├── versions.md                              # Changelog
├── .gitignore                               # Git ignore rules
└── README.md                                # This file
```

---

## Architecture

### Networks

**Frontend** (`frontend`):
- Traefik, Moodle, LTI tool, Jenkins, Prometheus, Grafana & cAdvisor
- Accessible from the host machine

**Backend** (`backend`):
- MariaDB (internal network, no internet access)
- Only Moodle can access it

### Security

- **Docker secrets** for sensitive data (not in environment variables)
- **Network isolation** (database not publicly reachable)

---

## References

- **Moodle documentation**: https://docs.moodle.org/
- **Traefik docs**: https://doc.traefik.io/traefik/
- **mkcert**: https://github.com/FiloSottile/mkcert

---

**Version**: See `versions.md` for changelog  
**Progress**: See `PROGRESS.md` for detailed project status  
**Author**: Neagu Sergiu
