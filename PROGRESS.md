# Project Voortgang

## Fase 1: Test Setup (KLAAR - 2025-11-19)
- [x] ltitest.yaml configuratie
- [x] MariaDB database met persistentie
- [x] Moodle 4.4 installatie werkend
- [x] LTI tool gebouwd en draaiend
- [x] LTI integratie getest en werkend
- [x] Docker netwerken geconfigureerd

**Toegang test setup:**
- Moodle: http://10.158.10.72:8080
- LTI Tool: http://10.158.10.72:5000
- Default login: user / bitnami
- Traefik: http://10.158.10.72:8081/dashboard/#/

**Test resultaat:**
LTI tool toont correct: User ID, Roles, Context ID

---

## Fase 2: Productie Setup (IN PROGRESS)
- [x] docker-compose.yaml met Traefik (Applicatie achter de reverse proxy zetten)
- [x] Secrets management configureren
- [x] Netwerk scheiding (frontend/backend)
        - Drontend: services die publiek bereikbaar moeten zijn (Traefik, Moodle, LTI) zitten hier.
        - Backend: interne netwerk alleen voor backend-services (database).   
- [x] Traefik reverse proxy werkend
- [x] Moodle bereikbaar via Traefik
- [x] LTI tool bereikbaar via Traefik op /lti path
- [ ] HTTPS configuratie met mkcert
- [x] Elke onderdeel van de applicatie in aparte container

---

## Fase 3: Jenkins CI/CD (TODO)
- [x] Jenkinsfile aanmaken
- [x] Docker images bouwen via Jenkins
- [x] Push naar Docker Hub
- [x] Automatische herdeployment

---

## Fase 4: Extra Features (TODO)
- [ ] Monitoring implementeren
- [ ] Health checks toevoegen
- [ ] [Kies één van de extra features uit opgave]

---

## Notities
- Bitnami Legacy images gebruikt zoals vereist
- Database credentials: bn_moodle / bitnami
- LTI OAuth secret: lti_oauth_secret

