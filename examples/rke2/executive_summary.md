🧾 Executive Summary: Automatizovaný deployment RKE2 clustra

🎯 Cieľ riešenia

Navrhujeme a realizujeme automatizované nasadenie Kubernetes clustrov (RKE2) v našej infraštruktúre, primárne na platforme Proxmox. Cieľom je vytvoriť udržiavateľnú, bezpečnú a flexibilnú platformu pre naše vývojové aj produkčné aplikácie – s dôrazom na automatizáciu, štandardizáciu a observabilitu.

⸻

🛠️ Čo budujeme v prvej fáze (lab/dev prostredie)
	•	Plne funkčný Kubernetes cluster postavený na RKE2
	•	Automatizovaný deployment cez Ansible + GitLab CI/CD
	•	Moderný storage riešený cez Longhorn s natívnym zálohovaním do S3
	•	Prístup do clustra cez VPN (WireGuard) + zabezpečenie cez Keycloak (RBAC)
	•	Monitoring a logovanie cez Grafana stack (Prometheus, Loki, InfluxDB)
	•	Dokumentovaný a testovateľný GitOps proces

⸻

🔍 Prečo RKE2 namiesto K3s?
	•	Stabilnejšie a bezpečnejšie riešenie vhodné pre produkčné použitie
	•	Plná kompatibilita s Kubernetes štandardom
	•	Vyššia možnosť integrácií a enterprise-level funkcií
	•	Vyhneme sa kompromisom, ktoré prináša „light“ alternatíva ako K3s
	•	Riešenie certifikované pre Goverment use s možnosťou dokúpenia vendor supportu, ale aj komerčných nadstavieb (securita, management, ...)   

⸻

🔄 Zálohovanie a prenositeľnosť
	•	Automatizované zálohy všetkých kľúčových komponentov (etcd, databázy, storage) do S3 úložiska
	•	Vďaka použitému stacku je systém ľahko prenositeľný do cloudu (AWS, Azure, či iné K8S distribúcie)

⸻

📊 Observabilita & Prístup
	•	Stav infraštruktúry a aplikácií je monitorovaný v reálnom čase
	•	Prístup ku grafom a logom je zabezpečený na úrovni tímov (RBAC)
	•	Všetko je konfigurovateľné a automatizovateľné

⸻

⏱️ Časový odhad a kapacity
	•	Fáza 1 (lab/prototyp): max. 10 MD (DevOps)
	•	Využívame už existujúce Ansible playbooky a knowhow (práca Martina)
	•	Výstupom bude overený, dokumentovaný a ľahko škálovateľný základ pre ďalšie prostredia

⸻

✅ Výhody pre firmu
	•	Nižšie prevádzkové náklady – všetko je automatizované
	•	Rýchlejšie nasadzovanie nových aplikácií a prostredí
	•	Lepšia bezpečnosť a dohľad nad infraštruktúrou
	•	Jednotný a opakovateľný postup pre všetky clustre a tímy
  	•	Odstránenie závyslostí a bottleneckov v Datalane