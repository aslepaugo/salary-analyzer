# Salary Analyzer
Search vacancies and pront average salaries in Moscow

## First Time preparations

Register application for SuperJob api usage - [registration page](https://api.superjob.ru/register).

Create `.env` file for local usage.

Add environment variable `SUPER_JOB_SECRET_KEY`

```bash
SUPER_JOB_SECRET_KEY = superjob_secret_key
```

Install requirements (Python 3 should be installed):

*Also, it's recommended to use virtual environment*

```bash
python -m venv venv
. ./venv/bin/activate
# or for Windows
# . .\venv\Scripts\activate
```

```bash
pip install -r requirements.txt
```

## Some tuning

There is constant list `PROGRAMMING_LANGUAGES` which consist predefined programming languages list. 
You can modify it to remove or add your own preferences.

## Run and Enjoy

To run script be sure you folowed preparation steps above.

```bash
python main.py

```

![Demo example](https://dvmn.org/filer/canonical/1567490703/266/)
