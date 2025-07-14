### Install packages


Create and activate a virtual environment:

```shell

python3 -m venv venv
source venv/bin/activate 
```

nstall packages

```shell
pip install -r requirements.txt

```

Vefify installation, i.e.

```shell
 python -c "import pandas as pd; print(pd.__version__)"
 python -c "import openai; print(openai.__version__)"  
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
