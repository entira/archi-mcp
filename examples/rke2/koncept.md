## 📄 Návrh riešenia: Automatizovaný deployment RKE2 clustra

### Manažérske zhrnutie

- **Strategický cieľ:** Zaviesť plne automatizovaný, opakovateľný a bezpečný proces nasadzovania Kubernetes clustrov v rámci našej on‑prem infraštruktúry.  
- **Hodnota pre biznis:** Rýchlejšie uvedenie služieb na trh, zníženie prevádzkových nákladov a zvýšenie spoľahlivosti.  
- **Rozsah projektu:** 10 MD DevOps kapacity s využitím existujúcich playbookov.  
- **Kľúčové míľniky:**  
  1. Lab deployment & validácia (T+2 týždne)  
  2. Integrácia CI/CD & GitOps (T+4 týždne)  
  3. Prezentácia výsledkov a schválenie pre produkciu (T+5 týždňov)


### 1. Úvod

**Cieľ dokumentu / Executive Purpose:**  
Popísať návrh a postup pre automatizovaný deployment Kubernetes clustra na báze RKE2 (Rancher Kubernetes Engine 2). Cieľom je zabezpečiť konzistentnú, opakovateľnú a jednoduchú inštaláciu clustrov v rámci infraštruktúry.

**Hlavné požiadavky:**  
- Automatizovaná inštalácia pomocou Ansible
- Podpora pre HA controlplane
- Kompatibilita s Proxmox clustrom
- GitOps prístup, CI/CD

**Prečo RKE2 namiesto K3s:**  
- RKE2 je plne kompatibilný s upstream Kubernetes, vrátane výstupných binárok a architektúry  
- Obsahuje vstavanú podporu pre pokročilé bezpečnostné funkcie ako SELinux, auditovanie, RBAC  
- Viac robustný pre produkčné použitie v prostredí software housu  
- Nevyžaduje kompromisy na úkor stability či funkcionality (na rozdiel od K3s)  
- Vyššia rozšíriteľnosť a lepšia integrácia s cloud-native toolingom (CNPG, Longhorn, cert-manager, atď.)
- Certifikované pre vládne použitie

### 2. Architektúra riešenia

**Komponenty:**
- RKE2 cluster – control-plane + workers
- Load balancer (HAProxy + Corosync/Keepalived) pre HA API
- MetalLB – loadbalancer pre on-prem
- WireGuard router pre VPN prístup
- Longhorn – distribuovaný storage
- CNPG – PostgreSQL operator s podporou S3 backupov
- cert-manager + Cloudflare DNS
- Rancher UI + Keycloak pre RBAC
- Grafana stack: Prometheus, Loki, InfluxDB

### 3. Deployment workflow (Ansible)

1. Naklonovanie Ansible repozitára
2. Práca vo vetve podľa prostredia (lab = voľnejšie ladenie, vyššie prostredia cez MR + review)
3. Merge request kontroluje maintainer, nesmie byť requester
4. Po schválení sa zmena dostane do `main` a spustí sa CI/CD
5. Ansible playbooky musia byť idempotentné
6. Denný cronjob kontroluje drifty – ak sa objaví zmena mimo Ansible, generuje alert

**Poznámka:** Každý Proxmox cluster má ručne nasadenú GitLab runner VM (nevytvára sa cez Ansible).

### 4. Požiadavky na infraštruktúru

1. Funkčný Proxmox cluster (root ssh prístup)
2. Jedna /24 sieť (napr. VLAN 192.168.100.0/24)
3. Dostatočné prostriedky
4. Doména s DNS a Cloudflare účtom

### 5. Storage architektúra

#### ❌ Ceph RBD (nevhodné)
- Bez zálohovania
- Komplexný na správu
- Nízka spoľahlivosť v našom prostredí

#### ✅ Longhorn
- cloud native storage
- Beží priamo na Kubernetes nodoch
- Nezávislé od typu storage backendu (ľahko migrovateľné)
- Podpora S3 backupov
- Web UI pre správu
- Observabilita cez Grafana stack

### 6. Zálohovanie

1. **etcd:** RKE2 nativne zálohuje do S3
2. **longhorn:** nativne zálohuje do S3
3. **CNPG (PostgreSQL):** nativne Scheduled + WAL backupy do S3

### 7. Observabilita (lab fáza)

- **Proxmox metriky:** Telegraf → InfluxDB v2 → Grafana
- **Logy:** Loki + Promtail, zobrazované v Grafane
- **RBAC:** Keycloak ako OIDC provider, prístup podľa namespace

### 8. Integrácia s Keycloak
- k8s namespace pristupy, managovane cez Rancher Webui (lahky provisioning, deprovisioning, aj kontrola manualnych zasahov)
- Grafana pristup - podla namespacov
- Po dodaní sa postup automatizuje (napr. ako Ansible role)

### 9. Ciele

- Deployment všetkých komponentov v Proxmox lab prostredí
- Kompletná dokumentácia (postupy, šablóny, skripty)
- GitOps workflow s CI/CD pipeline
- Observabilita pripravená pre dtlncloud

### 10. Kritériá úspechu

**Deploy clustra v dtlncloud** – meranie času od nuly po funkčný stav:

| Oblasť                | Metodika                                       | Cieľ                          |
|------------------------|------------------------------------------------|-------------------------------|
| Technická rýchlosť     | `time-to-cluster` od CI/CD po dostupný cluster| ≤ 45 min ideálne              |
| Observabilita          | Grafana zobrazuje metriky/logy                | do 10 min po deploy           |
| Dokumentácia           | Návody sú kompletné a testovateľné             | Peer-reviewed                 |
| Automatizácia          | Re-run playbookov nevedie k chybám (idempotencia) | Preukázané v lab teste    |

### 11. Odhad pracnosti

- **Rozsah prác:** max. **10 MD (mandayov)** DevOps kapacity  
- **Predpoklad:** Časť automatizácie (najmä Ansible playbooky) už existuje – vytvorené a udržiavané **Martinom**  
- Tieto playbooky budú:
  - Validované v lab prostredí
  - Prispôsobené pre nové komponenty (Longhorn, CNPG, cert-manager, WireGuard, observabilita)
  - Integrované do GitOps workflowu a CI/CD pipeline