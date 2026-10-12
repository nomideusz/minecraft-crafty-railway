# Deploy and Host Minecraft Java on Railway

[![Deploy on Railway](https://railway.com/button.svg)](https://railway.com/new/template/minecraft-java?referralCode=sLjDXb&utm_medium=integration&utm_source=button&utm_campaign=minecraft-java)

A Minecraft Java Edition server your friends can join a few minutes after you click deploy, run from a web panel instead of a terminal. The server is [Paper](https://papermc.io/), the fast, plugin-ready fork of the vanilla server. The panel is [Crafty Controller](https://craftycontrol.com/), where you get the live console, a file manager, players, backups and schedules in your browser.

## About Hosting Minecraft Java

It's one service, a Railway volume, and a TCP proxy for players.

- **Ready to join.** On first boot the template creates a Paper server on the newest release, points it at Railway's TCP proxy, and starts it. The memory it gets is sized to your plan.
- **Run it from the browser.** Use Crafty's panel for the console, config and file editing, plugin uploads, scheduled restarts and commands, and extra admin accounts with their own permissions.
- **Nightly backups.** At 04:00 UTC Crafty zips the server and keeps the last 3. Files Paper downloads again anyway are skipped, so a fresh world backs up in about 70 MB.
- **Survives redeploys.** On a redeploy Crafty saves the world and stops the server cleanly, then starts it again. Crash detection restarts it if it ever dies.

## Common Use Cases

- A private survival world for friends or family
- A Paper server with Bukkit/Spigot/Paper plugins
- A test bed for new versions and modpacks: Crafty can run more servers side by side

## Dependencies for Minecraft Java Hosting

- Railway's Hobby plan or above: Minecraft needs about 2 GB of memory

### Deployment Dependencies

- [Crafty Controller documentation](https://docs.craftycontrol.com/)
- [Paper documentation](https://docs.papermc.io/paper/)
- [Template source on GitHub](https://github.com/nomideusz/minecraft-crafty-railway)

### Implementation Details

**Join.** The address players need is in the Minecraft service's Settings → Networking, under TCP Proxy (something like `xyz.proxy.rlwy.net:12345`). It's also in the deploy logs, on the line starting "players join at". In Minecraft, go to Multiplayer → Add Server and paste it.

**Panel.** Open the service's Railway domain and sign in as `admin` with the `CRAFTY_ADMIN_PASSWORD` value from the Variables tab. After that you can change the password under Change Password in Crafty.

**Who can join.** A new server lets in anyone who has the address. To keep it to your friends, run `whitelist on` and then `whitelist add <player>` in the panel's Terminal.

**EULA.** Minecraft servers only run once you accept [Mojang's EULA](https://aka.ms/MinecraftEULA). You do that by setting `EULA` to `TRUE` when you deploy. If you didn't, set it now and redeploy, and the server is created then.

**Memory.** The server gets your plan's memory minus 1 GB, capped at 4 GB. Railway bills the memory actually used, which is about 2 GB for a fresh world and grows with players and view distance. To change the cap, edit `-Xmx` in the server's Config → Server Execution Command.

**Backups.** Backups are in the server's Backups tab: take one now, download, or restore. They live on the same volume as the world, so download one now and then for a copy off Railway. The volume starts at 5 GB; make it bigger in its settings if it fills up.

**Updates and plugins.** Update Server on the server's Config page downloads Paper again. For plugins, upload the `.jar` into the `plugins` folder in the Files tab, then restart.

**More servers.** Crafty can create more servers (Vanilla, Fabric, Forge, other versions). Each one needs its own port, and its own TCP proxy pointing at that port (Settings → Networking). Bedrock Edition and voice-chat mods use UDP, which Railway's TCP proxy can't carry.

## Why Deploy Minecraft Java on Railway?

Railway is a singular platform to deploy your infrastructure stack. Railway will host your infrastructure so you don't have to deal with configuration, while allowing you to vertically and horizontally scale it.

By deploying Minecraft Java on Railway, you are one step closer to supporting a complete full-stack application with minimal burden. Host your servers, databases, AI agents, and more on Railway.
