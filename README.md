# ![Recruiit](https://res.cloudinary.com/nogsantos/image/upload/v1583341771/recruiit/large_recruiit.png)

Workflow para análise e seleção de candidatos

## Setup

1. Create virtual env with `virtualenv`
2. Enable virtual env
3. Install dev dependencies
4. Migrate the database
5. Run the server

```console
virtualenv .recruiit -p python3
source .recruiit/bin/activate
pip install -r requirements-dev.txt
./manage.py migrate
./manage.py runserver
```

Access

http://127.0.0.1:8000/api/v1/health-check/

### Tools

**Lint**

```console
flake8 .
```

**tests-coverage**

```console
coverage run manage.py test -v 2 --noinput --failfast --parallel
coverage report -m
coverage html
```

## Publish

To publis on heroku [The Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)

1. Create an instance
2. Send configurations to Heroku
3. Defines a secret key to instance
4. Set DEBUG=False
5. Configure email send service
6. Send the code

```console
heroku create my-new-instance
heroku config:push
heroku config:set SECRET_KEY='python contrib/secret_gen.py'
heroku config:set DEBU=False
# email configurations
git push heroku master --force
```
