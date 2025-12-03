# Project Voortgang

## Fase 1: Test Setup (KLAAR - 2025-11-19)
- [x] ltitest.yaml configuratie
- [x] MariaDB database met persistentie
- [x] Moodle 4.4 installatie werkend
- [x] LTI tool gebouwd en draaiend
- [x] LTI integratie getest en werkend
- [x] Docker netwerken geconfigureerd

**Toegang test setup:**
- Moodle: https://10.158.10.72/
- LTI Tool: https://10.158.10.72/lti
- LTI Tool: https://10.158.10.72/lti/health (Health checks)
- Default login: user / bitnami
- Traefik: http://10.158.10.72:8081/dashboard/#/
- Traefik metrics: 
      - Grafana -> Dashboards -> Traefik
      - http://10.158.10.72:8081/metrics
      - In Prometheus query: traefik_entrypoint_requests_total 
- Jenkins: http://10.158.10.72/jenkins
- Prometheus: http://10.158.10.72:9090
- Prometheus metrics: http://10.158.10.72:9090/metrics
- Grafana: http://10.158.10.72:3000
- Node Exporter metrics: http://10.158.10.72:9100/metrics
- cAdvisor: http://10.158.10.72:8082
- cAdvizor metrics: http://10.158.10.72:8082/metrics

**Test resultaat:**
LTI tool toont correct: User ID, Roles, Context ID

---

## Fase 2: Productie Setup 
- [x] docker-compose.yaml met Traefik (Applicatie achter de reverse proxy zetten)
- [x] Secrets management configureren
- [x] Netwerk scheiding (frontend/backend)
        - Frontend: services die publiek bereikbaar moeten zijn (Traefik, Moodle, LTI) zitten hier.
        - Backend: interne netwerk alleen voor backend-services (database).   
- [x] Traefik reverse proxy werkend
- [x] Moodle bereikbaar via Traefik
- [x] LTI tool bereikbaar via Traefik op /lti path
- [x] HTTPS configuratie met mkcert
- [x] Elke onderdeel van de applicatie in aparte container

---

## Fase 3: Jenkins CI/CD 
- [x] Jenkinsfile aanmaken
- [x] Docker images bouwen via Jenkins
- [x] Push naar Docker Hub
- [x] GitHub integratie (automatische builds bij commits)
- [x] Automatische redeployment *(stage('Deploy') in Jenkinsfile)*

---

## Fase 4: Extra Features
- [x] Monitoring implementeren (Prometheus, Grafana, Node Exporter & cAdvisor)
      - Prometheus: http://10.158.10.72:9090
      - Grafana: http://10.158.10.72:3000
      - Node Exporter metrics: http://10.158.10.72:9100/metrics
      - cAdvisor: http://10.158.10.72:8082

- [x] Health checks toevoegen
- [x] Metrics voor traefiek toevoegen

---

## Notities
- Bitnami Legacy images gebruikt zoals vereist
- Database credentials: bn_moodle / bitnami
- LTI OAuth secret: lti_oauth_secret

