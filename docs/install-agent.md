# Dvredin build: laptop installation handoff for a local agent

## Goal and boundaries

Install **Dvredin's Untether 0.35.5rc15 snapshot** on the user's laptop. The laptop runs Codex; the user controls it from the **same private Telegram bot on a phone and in Telegram Desktop**. Do not install a second polling instance on the phone. No inbound port, router forwarding or public web server is needed for ordinary Telegram polling.

The laptop must be powered on, online and awake. Closing its lid or suspending it can stop remote access. Configure lid/sleep behaviour only after the user agrees; do not silently disable sleep or enable system-wide login lingering. A user service starts at login, not necessarily before login.

This handoff authorises setup of this bridge after the user asks you to install it. It does not authorise replacing another agent, changing existing provider/model/access policies, copying another person's credentials, or enabling public access.

## Pinned distribution

- Repository: <https://github.com/Dvredin/untether>
- Snapshot tag: `dvredin-v0.35.5rc15-1`
- Release: <https://github.com/Dvredin/untether/releases/tag/dvredin-v0.35.5rc15-1>
- Asset: `untether-0.35.5rc15-py3-none-any.whl`
- SHA-256: `0246b9eb9ef838819bfada532233cc3062de023d1dcd13420baf48c7a8f414d9`
- Python: 3.12 or newer.

Use the release wheel, **not** `uv tool install untether` from PyPI and **not** the repository's default branch. This is a prerelease snapshot of an existing installation, not an upstream stable release. Its runtime Python sources match the published source tree. Optional local Telegram Bot API support is included but is not required for this setup.

## 1. Discover the laptop and preserve existing work

Check the OS, current user, Python/uv, Codex CLI location/version and existing Untether processes/services. Do not print environment values, auth files, bot tokens or API keys. A status-only auth check is sufficient. Back up any existing Untether configuration/state privately before changing it. Do not overwrite a live service, reset conversations, remove lock files without verifying process ownership, or uninstall another agent.

Use an existing `uv` installation. If missing, use the maintained installation instructions at <https://docs.astral.sh/uv/getting-started/installation/> for the detected OS. Use Python 3.12+; `uv` can manage it without replacing the system Python.

These shell examples target Linux/macOS. On Windows, identify whether the user's existing Codex runs natively or under WSL, and install the bridge in the same environment. Do not create a parallel WSL setup or translate systemd commands into native Windows commands without checking the user's environment. macOS/Windows unattended startup needs the platform's own supervisor; the Linux unit below does not apply there.

## 2. Download, verify and install the exact wheel

Linux/macOS, in a private working directory:

```sh
curl --fail --location --connect-timeout 15 --max-time 180 \
  --output untether-0.35.5rc15-py3-none-any.whl \
  https://github.com/Dvredin/untether/releases/download/dvredin-v0.35.5rc15-1/untether-0.35.5rc15-py3-none-any.whl
```

Compute SHA-256 (`sha256sum` on Linux, `shasum -a 256` on macOS) and compare with the exact value above. Stop on mismatch. On an existing installation, drain active tasks before replacing the tool and keep its previous installation reference for rollback.

```sh
uv tool install --python 3.12 --force ./untether-0.35.5rc15-py3-none-any.whl
uv tool update-shell
```

Start a new shell if needed, then verify:

```sh
untether --version
```

Expected version: `0.35.5rc15`. The wheel hash and installation origin distinguish this fork snapshot from a different package with the same version. Keep the downloaded wheel and its checksum for reproducibility.

## 3. Reuse the user's existing Sub2API-connected Codex

**The intended path is the user's already working Codex CLI through Sub2API.** Reuse that installation, provider configuration and existing API key. Do not create another Sub2API client/key, require a new ChatGPT login or ask the user to repeat a completed broker setup. If the CLI is genuinely missing, install the official CLI using <https://github.com/openai/codex>; otherwise do not upgrade it just for this handoff.

Untether launches native Codex. It does not automatically inherit another agent's provider settings, and it does not invoke a shell alias/function called `codex`. Discover the actual executable, `CODEX_HOME`, active config/profile and any wrapper or one-off `-c` overrides used by the working CLI. Make the same effective route available to the process Untether actually starts.

Prefer the existing Codex config unchanged. Confirm its effective Sub2API base URL, current `model_provider` identifier, model/effort, Responses transport and credential alias. An identifier such as `codex_lb` can still point at Sub2API: preserve the identifier rather than renaming it for appearance. The existing broker key is sufficient; a special protected-input tool is **not** an installation prerequisite. Use the available local configuration/input workflow only if a value is actually missing. Do not publish or repeat key values in the installation report.

If the already working route is in a named profile, select **that same profile** in `~/.untether/untether.toml`:

```toml
[codex]
profile = "YOUR_EXISTING_CODEX_PROFILE"
```

Replace the placeholder with the verified existing name. If the working route is in the default Codex config, omit this table: no new profile is needed. Match the installed CLI's profile format. In current Codex 0.134.0+, `--profile NAME` overlays `CODEX_HOME/NAME.config.toml` using top-level keys, not a `[profiles.NAME]` table.

Only if native Codex itself is not yet connected, merge the user's existing Sub2API connection into its real user-level config. Use the existing endpoint and client credential on that laptop, `wire_api = "responses"`, `env_key` naming the existing credential variable and `requires_openai_auth = false` (or absent). `requires_openai_auth = true` ignores `env_key`. Preserve provider identity, model/effort and the existing native sandbox. Do not replace the whole config or change the other agent's provider settings. Public documentation deliberately does not include a personal endpoint or key.

**The service environment matters:** an exported key or `CODEX_HOME` available in the interactive terminal may be absent under systemd. Preserve the existing key alias and arrange for it and the actual `CODEX_HOME` to reach the Untether service and then the Codex child, using an existing local environment file/credential loader or the platform's supported equivalent. A wrapper/alias is not a substitute for checking the child process's actual route. Do not transfer a Telegram bot token as the model API key.

Before starting Telegram polling, test one small synthetic Codex request from the intended workspace using this actual executable/profile/environment. Verify the effective endpoint/provider/model, not merely the text of the answer. Recheck one request **under the service** in step 6. Keep existing conversations and auth; no logout or reset is needed.

Configuration reference: [Codex advanced configuration](https://learn.chatgpt.com/docs/config-file/config-advanced) and [provider authentication](https://learn.chatgpt.com/docs/auth).

## 4. Create a separate private Telegram bot

Use the user's dedicated Untether bot if already prepared; otherwise help them create one with <https://t.me/BotFather> (`/newbot`). Enter its token using the local onboarding wizard or the available local configuration workflow. A special protected-input tool is not required. Do not reuse another running agent's bot token: only one polling process can serve the same bot. The phone needs only Telegram, not Python or Codex.

Choose a dedicated working directory, for example `~/untether-workspace`, rather than running the agent in the entire home directory. Run onboarding interactively from that directory:

```sh
untether --onboard
```

Select:

1. The new dedicated bot token.
2. **Assistant** mode: one ongoing private conversation.
3. Open that bot from the user's Telegram account and send `/start` when the wizard waits for the chat.
4. Default engine **Codex**.
5. Save the configuration.

The wizard generates the bot's `chat_id` and `allowed_user_ids`. Verify that the allowlist contains only the intended user's Telegram user ID, `allow_any_user` stays false, `session_mode` is `chat`, and topics are disabled. Never paste the full token-bearing configuration into a report. Restrict the config directory to its owner and the configuration file to owner read/write permissions.

This rc15 build's Codex **Safe** mode is an exec-level **read-only sandbox**, not interactive tool-approval buttons. Start the private setup in Safe mode through `/config` before the first task. If the user needs file changes, explain the effective native sandbox/automatic-execution policy and obtain their decision before switching. Do not add sandbox-bypass flags to `extra_args`; rc15 rejects them. A full-access native profile is not part of this installation's default requirements.

Use the public Telegram Bot API defaults. Do not enable a custom/local Bot API endpoint or enlarge file limits for ordinary phone access. Voice transcription is optional and needs a separately configured supported transcription service/key; text and photo support do not imply voice is configured. Do not activate paid transcription or scheduled tasks without approval.

## 5. Prove phone and computer access before autostart

Keep just one bridge process running. Send these tests from the user's own private bot chat:

- `/ping`: receive a live response.
- Ask for a harmless answer containing a distinctive made-up marker; verify a final Codex answer, not only a progress message.
- Send a follow-up asking for that marker without a reply; verify the conversation continues.
- Open **the same bot and same account in Telegram Desktop**; verify the conversation is visible there and a new harmless message gets an answer.
- Send a small non-sensitive test photo and ask what it shows if photo support is needed.

Phone and Telegram Desktop are two views of the same conversation, not independent agent sessions. `/new` resets this chat's agent session; `/cancel` stops the current run. If a test fails, resolve it before claiming completion. Do not fabricate Telegram delivery or continuity results.

## 6. Linux autostart, after the foreground test passes

Use a **user** systemd service. Preserve any existing unit and choose a different name if it belongs to another bridge. Base the unit on [the upstream template](../contrib/untether.service), but adapt it to the actual installation:

- `ExecStart`: absolute path reported by `command -v untether`.
- `WorkingDirectory`: the dedicated workspace used in the foreground test.
- `Type=notify`, `NotifyAccess=main`, `Restart=always`, `RestartSec=2`, `KillMode=mixed`, `TimeoutStopSec=150`.
- `HOME` and `PATH`: the correct user home and paths containing both Untether and the actual Codex executable, including an nvm/other managed install if applicable.
- The template's `EnvironmentFile=%h/.untether/.env` is mandatory unless adapted. **Omit it when no environment file is required**; if one is required for the approved Codex credential, create it privately with mode 0600. Do not dump the interactive shell's whole environment into it.
- Keep the Telegram token in the private configuration, not in `ExecStart`, command history or a public unit.
- Preserve the existing Sub2API credential alias and the working CLI's `CODEX_HOME`, model/provider/profile and executable path in the service environment. Do not assume shell exports, aliases or nvm paths are automatically inherited.

Stop/drain the foreground bridge first, so the unit is the only polling process. For a newly created `untether.service`:

```sh
systemctl --user daemon-reload
systemctl --user enable --now untether.service
systemctl --user is-enabled untether.service
systemctl --user is-active untether.service
```

Re-run `/ping` and one harmless Codex request from the phone **under the service**, since its PATH/auth environment can differ from the interactive shell. Verify the service starts after a user login and explain the laptop sleep/lid limitation. Do not edit sleep settings or enable lingering without agreement.

On macOS/native Windows, keep the verified foreground result and configure an appropriate per-user supervisor only for that platform and with permission. Clearly report if unattended startup remains incomplete.

## 7. Updates, rollback and completion receipt

Do not use a generic `uv tool upgrade untether`: it may replace this fork with an upstream distribution and remove its patches. Update only to another explicitly selected Dvredin release asset, with its checksum, preserving config/state and draining active tasks. The tag is immutable; do not move it or replace the wheel in place.

Rollback means restoring the previous tool installation reference and only the configurations changed by this setup. Never restore stale polling offsets or overwrite newer conversation state blindly.

Report only: detected OS, installed wheel hash/version, Codex version/profile/provider alias (no credentials), dedicated bot link, workspace, startup method, successful phone/Telegram Desktop/continuity tests, and anything actually unfinished. Do not say 'done' from package installation or an active PID alone.
