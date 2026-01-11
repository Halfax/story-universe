# AGENTS.md

## Build/Test Commands
<!-- Add commands as project develops -->
<!-- Example: npm test -- path/to/test.ts (single test) -->

## Architecture
This is a new project. Document structure here as it develops.

## Code Style
- Use consistent formatting (Prettier/ESLint recommended)
- Prefer explicit types over `any`
- Use descriptive variable/function names
- Handle errors explicitly, avoid silent failures
- Group imports: external deps, then internal modules

## Conventions
- Keep functions small and focused
- Write tests alongside new features
- Document public APIs

## Startup on Reboot
This project includes a small helper and cron entry to start the `chronicle-keeper` Docker container automatically on system reboot.

- **Files:**
	- [story-universe/chronicle-keeper/scripts/start_on_boot.sh](story-universe/chronicle-keeper/scripts/start_on_boot.sh#L1-L200) — startup helper that waits briefly and ensures the container is running or starts it.
	- [story-universe/chronicle-keeper/cron/chronicle-keeper](story-universe/chronicle-keeper/cron/chronicle-keeper#L1-L50) — cron.d entry that runs the helper on `@reboot` as `root`.
	- [story-universe/chronicle-keeper/scripts/install_cron.sh](story-universe/chronicle-keeper/scripts/install_cron.sh#L1-L200) — installer script to copy the cron file into `/etc/cron.d/` and set permissions.

- **Install (run on host):**

```sh
sudo chmod +x story-universe/chronicle-keeper/scripts/start_on_boot.sh
sudo story-universe/chronicle-keeper/scripts/install_cron.sh
```

- **What it does:** The helper will start the container with `docker run -d --name chronicle-keeper --restart unless-stopped -p 8001:8001 chronicle-keeper` if the container doesn't already exist or run, and the cron entry ensures the helper runs at every reboot.

If you prefer a `systemd` service instead of `cron.d`, say so and I will add a unit file.
