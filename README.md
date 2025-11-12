[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/5TKraKfR)
Voor de projectopdracht 25-26 zet je een Moodle 4.4 installatie op op je Bletchley machine. Moodle is het achterliggende onderwijsplatform waarop DigitAP bouwt. Je doet dit aan de hand van [de Bitnami (Legacy) Moodle image](https://hub.docker.com/r/bitnamilegacy/moodle). Je Moodle zal ook integreren met een "LTI-app". Dit is een externe applicatie die je in Moodle kan presenteren alsof het een onderdeel van een cursus is. Verder zijn er een aantal extra aandachtspunten:
- je vindt op [Panopto](https://ap.cloud.panopto.eu/Panopto/Pages/Viewer.aspx?id=3911da00-daab-4e76-a5c0-b39201524359) een instructiefilmpje rond het gebruik van de LTI-app
- op de Docker Hub pagina bitnamilegacy/moodle vind je niet veel info, maar op bitnami/moodle vind je de nodige info wel
- je voorziet persistentie van de Moodle installatie door middel van de nodige volumes en een database
- je maakt ook de gegeven "LTI-applicatie" onderdeel van je Docker Compose setup en zet deze (in de productiesetup) achter je reverse proxy
- wanneer je je repository pusht, bouwt Jenkins het geheel, pusht hij je Docker images naar je persoonlijke Docker Hub account en herdeployt hij de Moodle stack
- je maakt **twee** Docker Compose files:
  - ltitest.yaml (om de Moodle installatie en de LTI app samen als één stack te laten lopen, zonder Traefik en zonder Jenkins, zodat je makkelijk kan testen dat de LTI-app wel werkt; zorg dat je deze eerst aan de praat hebt voor je aan de productiesetup begint)
  - docker-compose.yaml (voor de productiesetup, met mooi gescheiden netwerken, secrets, enzovoort)
    - normaal zou je LetsEncrypt gebruiken voor een SSL-certificaat, maar omdat je machine niet op het publieke Internet staat gebruik je [mkcert](https://github.com/FiloSottile/mkcert)
- je houdt je werk bij in een Git repository met duidelijke commit messages (zowel de regelmaat als de kwaliteit van je commits wordt beoordeeld)
- voor het basiscijfer moet je de testsetup plus een goed gedeployde Moodle hebben die via Jenkins herstart wordt en moet je "best practices" rond versiebeheer en organisatie van netwerken, secrets,...
  - correcte configuratie van HTTPS is een mooie extra
  - een werkende LTI-app in de productiesetup is een mooie extra
  - verdere ideeën voor nuttige extra's zijn:
    - een dev container specifiek om aan de LTI-applicatie te werken
    - profiling van de applicatie (welke stappen duren het langst wanneer we bepaalde operaties uitvoeren)
	- automatiseren van de aanmaak van een cursus
	- automatiseren van de installatie van een Moodle plugin
	- health checks voor de hele setup
Vrijwel alles wat je hiervoor moet doen staat op Docker Hub en in de documentatie van Jenkins en Traefik. Secundaire bronnen zijn niet even betrouwbaar. Je mag LLM's gebruiken maar je moet de dwaalsporen erbij nemen.
