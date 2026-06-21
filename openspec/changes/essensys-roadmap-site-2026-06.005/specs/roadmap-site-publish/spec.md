# roadmap-site-publish

## ADDED Requirements

### Requirement: Public roadmap site

The system SHALL publish a static site at `https://roadmap.essensys.fr` listing OpenSpec product changes grouped as in-progress, completed, and upcoming with detailed descriptions sourced from OpenSpec artifacts.

#### Scenario: Visitor browses active changes

- **WHEN** a visitor opens `https://roadmap.essensys.fr`
- **THEN** they see all changes with status **active** ordered by `roadmap_id`
- **AND** each entry links to a detail page with proposal excerpt, dependencies, and host repo

#### Scenario: Site reflects git truth

- **WHEN** an OpenSpec change status changes in `essensys-memory` on `main`
- **AND** CI or deploy runs within 24 hours
- **THEN** the public site shows the updated status

### Requirement: Blog on support site

The system SHALL expose a blog section at `https://mon.essensys.fr/blog` fed from Markdown in `essensys-memory/content/blog/`.

#### Scenario: Significant epic advancement

- **WHEN** a significant OpenSpec epic becomes active or completed
- **THEN** a blog post is added with title, roadmap_id, narrative, and optional screenshots
- **AND** the post appears on `/blog` after the next support-site build

#### Scenario: Screenshot capture workflow

- **WHEN** an agent authors a blog post for a UI-visible milestone
- **THEN** screenshots are captured via Chrome DevTools MCP
- **AND** stored under `raw/assets/roadmap-blog/` and referenced in post frontmatter

### Requirement: Queue execution publishes public sites

After every OpenSpec queue review execution (`prompts/roadmap-product.md` Step E) or user-visible product change, agents SHALL run `publish-roadmap-public.sh` to regenerate https://roadmap.essensys.fr and prepare https://mon.essensys.fr/blog.

#### Scenario: Roadmap product prompt completed

- **WHEN** an agent finishes updating the OpenSpec queue or product roadmap
- **THEN** it runs `essensys-memory/scripts/publish-roadmap-public.sh`
- **AND** verifies or documents deploy status for both public URLs

#### Scenario: User-visible feature shipped

- **WHEN** a queued epic produces a change visible on support-site, portal, docs, or gateway UI
- **THEN** the agent captures screenshots via Chrome DevTools MCP
- **AND** adds or updates a blog post before or immediately after publish

### Requirement: Agent sync rule

Agents SHALL resynchronize the roadmap site and evaluate blog post need on every significant OpenSpec advancement per `essensys-roadmap-site.mdc`.

#### Scenario: Change completed

- **WHEN** all tasks in an OpenSpec change are checked complete
- **THEN** the agent regenerates roadmap site content
- **AND** publishes a closure blog post if the epic was significant

### Requirement: Ansible OVH deployment

The roadmap public site SHALL be deployable to production via Ansible playbook `deploy-roadmap-site.yml` and role `roadmap_site` per spec `roadmap-site-ansible`.

#### Scenario: Operator deploys roadmap site

- **WHEN** `ansible-playbook deploy-roadmap-site.yml -i inventory/ovh` succeeds
- **THEN** `https://roadmap.essensys.fr` serves the latest built static content from `/opt/essensys/roadmap-site/`

#### Scenario: Redeploy after queue sync

- **WHEN** `publish-roadmap-public.sh` updates content and the playbook is re-run
- **THEN** production reflects the new OpenSpec queue without manual file edits on the VPS
