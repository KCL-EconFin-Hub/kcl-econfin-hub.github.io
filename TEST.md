# Deploying the test instance

How to put a password-protected test copy of the site at
**https://efh-test.edwinlock.com**, so others can review changes before they go
live. Production stays on GitHub Pages; the test copy is separate and is never
linked from it.

The site is static: Jekyll builds it into plain files in `_site/`, and nginx
serves those files from `/home/ubuntu/finance-hub-test/` behind HTTP basic
authentication. The password protection lives entirely in the nginx
configuration; nothing in the site changes.

This assumes an Ubuntu server with nginx installed and SSH access as the
`ubuntu` user. Replace `reviewer` with whatever username you want to give
reviewers.

## 1. Point the subdomain at the server

Wherever `edwinlock.com`'s DNS is managed, add an **A record** for `efh-test`
pointing at the server's IPv4 address, **91.99.230.96**. (An AAAA record is
only needed if you also want the site reachable over IPv6.) Check it has
taken effect:

```bash
dig +short efh-test.edwinlock.com     # should print 91.99.230.96
```

Until it does, you can use `ubuntu@91.99.230.96` instead of
`ubuntu@efh-test.edwinlock.com` for SSH and rsync.

## 2. Build the site

On your own machine, in the repository:

```bash
bundle exec jekyll build
```

This writes the site to `_site/`. The upcoming/past split of events is worked
out at build time, so rebuild to refresh it. This build runs in development
mode, so the test copy never includes the Umami analytics tag and visits to
it aren't counted.

## 3. Copy the files to the server

```bash
rsync -avz --delete _site/ ubuntu@efh-test.edwinlock.com:/home/ubuntu/finance-hub-test/
```

rsync creates the folder the first time. A few details:

- The trailing slash on `_site/` matters: it copies the folder's *contents*.
- `--delete` removes files that no longer exist in the build.
- `-a` keeps the files' permissions, and Jekyll builds them readable by
  everyone, which nginx needs.

## 4. Let nginx into the home directory

nginx runs as the `www-data` user. Ubuntu's home directories are private by
default, so nginx can't reach `/home/ubuntu/finance-hub-test/` and would answer
"403 Forbidden". On the server, allow `www-data` (and nobody else) to pass
through `/home/ubuntu`, without being able to list or read anything else in it:

```bash
sudo apt install acl                          # usually already installed
sudo setfacl -m u:www-data:x /home/ubuntu
```

To check, `sudo -u www-data cat /home/ubuntu/finance-hub-test/index.html`
should print the page.

## 5. Create a password file

On the server:

```bash
sudo apt install apache2-utils                                     # provides htpasswd
sudo htpasswd -c /etc/nginx/finance-hub-test.htpasswd reviewer     # prompts for a password
sudo chown root:www-data /etc/nginx/finance-hub-test.htpasswd
sudo chmod 640 /etc/nginx/finance-hub-test.htpasswd
```

`-c` creates the file. Use it **only the first time**, because it overwrites
an existing file. To add more reviewers later:

```bash
sudo htpasswd /etc/nginx/finance-hub-test.htpasswd alice      # add or change a user
sudo htpasswd -D /etc/nginx/finance-hub-test.htpasswd alice   # remove a user
```

nginx rereads the file on each request, so no reload is needed.

## 6. Configure nginx

Create `/etc/nginx/sites-available/finance-hub-test`:

```nginx
server {
    listen 80;
    listen [::]:80;
    server_name efh-test.edwinlock.com;

    root /home/ubuntu/finance-hub-test;
    index index.html;

    auth_basic "Economics and Finance Hub (test)";
    auth_basic_user_file /etc/nginx/finance-hub-test.htpasswd;

    # Keep the test copy out of search engines.
    add_header X-Robots-Tag "noindex, nofollow" always;

    location / {
        try_files $uri $uri/ =404;
    }
}
```

Enable it and reload:

```bash
sudo ln -s /etc/nginx/sites-available/finance-hub-test /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

## 7. Turn on HTTPS

**Don't skip this step.** Basic authentication sends the password with every
request, only base64-encoded. Without HTTPS anyone on the network can read
it.

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d efh-test.edwinlock.com
```

Certbot gets a certificate from Let's Encrypt, adds it to the server block,
redirects HTTP to HTTPS and renews itself automatically. Ports 80 and 443
must be open in the server's firewall (and in the Hetzner Cloud Firewall, if
you use one).

## 8. Check it works

```bash
curl -sI https://efh-test.edwinlock.com/ | head -1                       # expect 401
curl -sI -u reviewer:PASSWORD https://efh-test.edwinlock.com/ | head -1  # expect 200
```

Then open https://efh-test.edwinlock.com in a browser and log in. Check that:

- the page is styled (if not, see Troubleshooting)
- Overview, Events and Software all load
- the "Add to calendar" button downloads a file (if there are events)

## Updating the test copy

Rebuild and copy again:

```bash
bundle exec jekyll build && rsync -avz --delete _site/ ubuntu@efh-test.edwinlock.com:/home/ubuntu/finance-hub-test/
```

## Removing it

On the server:

```bash
sudo rm /etc/nginx/sites-enabled/finance-hub-test /etc/nginx/sites-available/finance-hub-test
sudo nginx -t && sudo systemctl reload nginx
sudo certbot delete --cert-name efh-test.edwinlock.com
sudo rm /etc/nginx/finance-hub-test.htpasswd
rm -r /home/ubuntu/finance-hub-test
sudo setfacl -x u:www-data /home/ubuntu       # if nothing else nginx serves lives there
```

Then delete the DNS record.

## Troubleshooting

| Symptom | Likely cause |
| --- | --- |
| Browser can't connect | DNS hasn't taken effect yet (step 1), or ports 80/443 are blocked by a firewall. |
| Another site appears instead | nginx didn't match `server_name`. Check that the site is linked in `sites-enabled` and that `nginx -t` passes. |
| 403 Forbidden after logging in | nginx can't reach the files. Redo step 4 and check that `sudo -u www-data cat /home/ubuntu/finance-hub-test/index.html` works. If it doesn't, make the files readable with `chmod -R a+rX /home/ubuntu/finance-hub-test`. |
| 500 Internal Server Error | nginx can't read the password file. Check its owner and mode (step 5). |
| Password prompt keeps coming back | Wrong user or password, or the file was overwritten by a second `htpasswd -c`. |
| Certbot fails | Usually DNS not yet pointing at the server, or port 80 blocked. |
| `nginx -t` fails | The message gives the file and line. Usually a missing `;` or `}`. |
