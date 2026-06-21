# roadmap-site-ansible

## ADDED Requirements

### Requirement: Ansible role roadmap_site

The system SHALL provide an Ansible role `essensys-ansible/roles/roadmap_site/` that builds and deploys the static roadmap site to the OVH VPS, mirroring the pattern of `roles/docs_site/`.

#### Scenario: Deploy from control node

- **WHEN** an operator runs `ansible-playbook deploy-roadmap-site.yml -i inventory/ovh`
- **THEN** the role clones `essensys-memory`, runs `scripts/build-roadmap-site.sh`, copies output to `/opt/essensys/roadmap-site/`
- **AND** configures Nginx vhost `essensys-roadmap` for `roadmap.essensys.fr`

#### Scenario: Idempotent redeploy after queue update

- **WHEN** OpenSpec queue content changes on `essensys-memory` main
- **AND** the playbook is re-run
- **THEN** the public site content is updated without manual SSH edits

### Requirement: TLS and DNS

The deployment SHALL obtain a Let's Encrypt certificate for `roadmap.essensys.fr` when DNS resolves to the VPS, using the same certbot webroot flow as `docs_site`.

#### Scenario: DNS ready

- **WHEN** `roadmap.essensys.fr` A/AAAA record points to the OVH host
- **THEN** certbot succeeds and Nginx serves HTTPS on port 443

#### Scenario: DNS not ready

- **WHEN** DNS is not configured
- **THEN** the role deploys HTTP-only on port 80
- **AND** the playbook completes without failure (certbot `failed_when: false`)

### Requirement: Blog deploy via support-site

Blog content at `https://mon.essensys.fr/blog` SHALL be deployed by rebuilding the support-site frontend (role `frontend`) after `prepare-blog.sh`, not by a separate Nginx vhost.

#### Scenario: Full public surfaces deploy

- **WHEN** operator runs `deploy-roadmap-site.yml`
- **THEN** playbook applies roles `roadmap_site` then `frontend` (blog static assets in SPA `dist/`)

### Requirement: CI artifact deploy path

The Ansible role SHALL support deploying from a pre-built CI artifact when `roadmap_site_use_ci_artifact: true`, skipping on-host MkDocs build as documented in `design.md`.

#### Scenario: CI-first deploy

- **WHEN** CI publishes `roadmap-site.tar.gz` as workflow artifact
- **THEN** Ansible role copies the artifact to `roadmap_site_root` without running `build-roadmap-site.sh` on the VPS
