# SprintSync

An Agile team backlog and communication bot for the IT26210 (DEVASC) final project by **Kwatro Kantos**.

SprintSync reads the team's Trello backlog through the Trello REST API and posts daily stand-up reminders, task updates, and Jenkins build results to the team's Webex space.

## Team

| Member | Scrum role | Module |
| --- | --- | --- |
| Verrill M. Bargola | Scrum Leader | `main.py`, repository |
| Abraham Y. Ileto | Developer | `trello_client.py`, `device_status.py` |
| John Reymond G. Pascual | Developer, QA | `config.py`, `webex_client.py`, `notify.py`, tests, Jenkinsfile |
| Albert John C. Vendiola | Recorder | `formatter.py`, README |

## Project structure

```
sprintsync/
├── sprintsync/
│   ├── config.py          # loads .env settings
│   ├── main.py            # CLI menu and arguments, stand-up job
│   ├── trello_client.py   # Trello REST API calls and JSON parsing
│   ├── webex_client.py    # Webex Messages API calls
│   ├── formatter.py       # builds Markdown messages
│   ├── device_status.py   # NETCONF interface status (optional)
│   └── notify.py          # posts Jenkins build results to Webex
├── tests/                 # pytest unit tests with mocked responses
├── Jenkinsfile
├── requirements.txt
└── .env.example
```

## Setup

```
git clone https://github.com/VerrillB/Sprintsync.git
cd Sprintsync
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # Linux or macOS
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill in your Trello and Webex values. Never commit `.env`.

## Usage

```
python -m sprintsync.main --standup    # post the stand-up to Webex
python -m sprintsync.main --backlog    # print the backlog in the terminal
python -m sprintsync.main --menu       # interactive menu
```

## Testing

```
pytest
flake8 sprintsync tests
```

## CI/CD

Jenkins runs the Jenkinsfile on every commit to `main`: install, lint, unit test, then post the result to Webex.
