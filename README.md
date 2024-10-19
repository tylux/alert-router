# Alert Router

Take a config and routes alerts to slack channels based on substring matches, if no match is found fallback to a defined channel


# Setup 

```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Startup
```
gunicorn -b 0.0.0.0:8000 main:app
```

TODO

* docstrings
* log levels
* test with real datadog payload
    * Parse things like tags, team etc that might come with this
* Secure endpoint
* tests
* dockerfile
* lint
* ci

