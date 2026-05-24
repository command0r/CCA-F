# S02-L04 — Watch The Loop Break, Then Watch It Stop

Demo accompanying Lecture 2.4 of the CCA-F course.

## Setup

    python -m venv .venv
    source .venv/bin/activate           # Windows: .venv\Scripts\activate
    pip install -r requirements.txt
    cp .env.example .env                # then paste your key into .env

## Run

    python agent.py broken              # silent-failure tool — loops until safety cap
    python agent.py fixed               # structured-error tool — terminates at iter 1

The deliberate break is in `tools_broken.py`. The fix is in `tools_fixed.py`. The agent code (`agent.py`) is identical in both runs.