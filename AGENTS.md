# AGENTS.md

## Build/Test Commands
<!-- Add commands as project develops -->
<!-- Example: npm test -- path/to/test.ts (single test) -->

**Virtual environments:** The preferred venv for development is the repo-level `./venv` at the repository root. Component-level venvs (from older layouts) may exist in subfolders — prefer the root venv for consistency.
	- On Windows (PowerShell): `venv\Scripts\Activate.ps1` or `venv\Scripts\activate` (cmd).
	- On Linux/macOS: `source venv/bin/activate`.
	- Install dependencies and run tests from the root with (PowerShell example):

		$env:PYTHONPATH='src'; .\venv\Scripts\python.exe -m unittest discover -s tests -v

	  Or (POSIX):

		PYTHONPATH=src ./venv/bin/python -m unittest discover -s tests -v

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

**Startup on reboot / host helpers:**

Some deployment helpers (startup scripts, cron entries) previously lived under component folders before the repo layout was flattened. The authoritative locations and installer scripts were moved or consolidated. See `docs/REPO_LAYOUT_CHANGE.md` for exact file moves.

If you need to install a startup helper on the host, copy the current script into `/etc/cron.d/` or create a `systemd` unit. Example (update paths to match your host layout):

```powershell
sudo chmod +x ./tools/start_on_boot.sh
sudo ./tools/install_cron.sh
```

Or create a `systemd` unit pointing to the container `docker run` command shown below.

**What it does:** The helper starts the `chronicle-keeper` container with:

```
docker run -d --name chronicle-keeper --restart unless-stopped -p 8001:8001 chronicle-keeper
```

If you prefer a `systemd` service instead of `cron.d`, say so and I will add a unit file and a host installation guide.

## Agent Tracker Sync


Note: The repository layout was flattened on 2026-01-13. See [docs/REPO_LAYOUT_CHANGE.md](docs/REPO_LAYOUT_CHANGE.md) for details on the new `src/` and `tests/` layout.
