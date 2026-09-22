# Pinned: a silent upstream rebase would hit every deploy of this template at once.
FROM registry.gitlab.com/crafty-controller/crafty-4:4.11.0

# Crafty serves its panel over HTTPS only (self-signed, :8443) and Railway's edge
# talks plain HTTP to the container, so Caddy sits in between on $PORT.
COPY --from=caddy:2.11.4 /usr/bin/caddy /usr/bin/caddy
COPY Caddyfile /etc/caddy/Caddyfile
COPY --chmod=0755 railway-entrypoint.sh /railway-entrypoint.sh
COPY --chmod=0755 first-server.py /first-server.py

# Railway gives a service one volume, mounted at /data; every path Crafty keeps
# state in points there. Crafty saves its servers directory as given, then compares
# it with resolved paths (file manager, backup exclusions): give it the real one,
# both as the default and as what it stores on first start.
RUN ln -s /data/config /crafty/app/config \
 && for d in servers backups logs import; do ln -s /data/$d /crafty/$d; done \
 && sed -i 's|os.path.join(self.root_dir, "servers")|os.path.realpath(&)|' /crafty/app/classes/helpers/helpers.py \
 && sed -i 's|os.path.join(controller.project_root, "servers")|os.path.realpath(&)|' /crafty/main.py \
 && grep -q 'realpath(os.path.join(self.root_dir, "servers"))' /crafty/app/classes/helpers/helpers.py \
 && grep -q 'realpath(os.path.join(controller.project_root, "servers"))' /crafty/main.py

ENTRYPOINT ["/railway-entrypoint.sh"]
