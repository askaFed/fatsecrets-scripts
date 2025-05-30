### Install packages

```shell
python3 -m pip install --user pandas requests requests-oauthlib python-dotenv psycopg2-binary

```

Vefify installation

```shell
python3 -c "import pandas as pd; print(pd.__version__)"

```

### Run scripts in cron

Open crontab

```shell
crontab -e

```

Add rules

```shell

17 * * * * ./run_hourly.sh

```
