# CGS - Cloud Game Save Software
The problem with linux gaming via launchers like Heroic, Lutris and Faugus is that there are no cloud saves. If I play the same game on a different machine I need to start from first level. So I built my own cloud game save software.

### Features
- Continuous file monitoring via watchdogs
- Custom sync logic
- SeaweedFS + S3 integration

### Tech Stack
FastAPI, PostgreSQL, Asyncpg, SeaweedFS, AWS S3, Docker Compose

### Architecture
![CGS architecture](/Architecture.png)

### Setup
Prerequisites
- Python (with a virtual environment) for FastAPI
- PostgreSQL running on localhost
- Docker, for running SeaweedFS in a container


### 1. Install dependencies
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Set up PostgreSQL
On Fedora, PostgreSQL's default authentication method (`peer`/`ident`) will block creating a database user. Edit `pg_hba.conf` and change the authentication method for IPv4 and IPv6 addresses to `scram-sha-256`, then restart PostgreSQL.

Then create a custom database user and database:
```bash
sudo -u postgres psql
CREATE USER myuser WITH PASSWORD 'mypassword';
CREATE DATABASE myapp OWNER myuser;
```

### 3. Environment variables
- `DB_USER` : Database user
- `DB_PASSW` : Database password
- `CONFIG_FILE` : Path to config file
- `SEAWEEDFS` : SeaweedFS filer HTTP address
- `AWS_ACCESS_KEY_ID` : IAM user access key with access to the S3 bucket
- `AWS_SECRET_ACCESS_KEY` : IAM user secret access key with access to the S3 bucket
- `AWS_REGION` : Region where the S3 bucket is hosted
- `S3_BUCKET_NAME` : Name of the S3 bucket

`CONFIG_FILE` points to a JSON file containing the relative path of the folder to be synced.

### 4. Start SeaweedFS
```bash
docker compose up -d seaweedfs
```

### 5. One-time AWS S3 integration
Load the environment variables in your terminal, then run:
```bash
docker compose exec -T seaweedfs weed shell <<EOF
remote.configure -name=aws1 -type=s3 -s3.access_key=$AWS_ACCESS_KEY_ID -s3.secret_key=$AWS_SECRET_ACCESS_KEY -s3.region=$AWS_REGION
remote.mount -dir=/upload/MGS -remote=aws1/$S3_BUCKET_NAME/MGS -nonempty
remote.meta.sync -dir=/upload/MGS
remote.copy.local -dir=/upload/MGS
exit
EOF
```
`MGS` is the master folder where game saves are put into — replace it with the folder name you're syncing, matching your config file.

### 6. Run
```bash
uvicorn backend.main:app --reload
```

### Limitations
- No user sessions. A single user id is hardcoded wherever needed
- Sync function assumes a single concurrent user
- Conflict resolution is just latest modified time wins
- No automated tests or retries
- Rapid burst of inotify events causes the watchdog observer thread to stop

### Future Work
- Dedicated user sessions
- Desktop client
- Multi user sync support