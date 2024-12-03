import sys

from invoke import task


@task
def start_development(ctx):
    if sys.platform != "win32":
        ctx.run("FLASK_ENV='development' python3 -m src.app.index", pty=True)
    else:
        ctx.run("set FLASK_ENV='development' && python -m src.app.index")


@task
def start_production(ctx):
    if sys.platform != "win32":
        ctx.run(
            "FLASK_ENV='production' gunicorn --config gunicorn_config.py src.app:app",
            pty=True,
        )
    else:
        ctx.run("set FLASK_ENV='production' && python -m src.app.index")


@task
def start_test_environment(ctx):
    if sys.platform != "win32":
        ctx.run("FLASK_ENV='testing' python3 -m src.app.index", pty=True)
    else:
        ctx.run("set FLASK_ENV='testing' && python -m src.app.index")


@task(start_test_environment)
def test(ctx):
    ctx.run("pytest")


@task
def coverage(ctx):
    if sys.platform != "win32":
        ctx.run("coverage run --branch -m pytest", pty=True)
    else:
        ctx.run("coverage run --branch -m pytest")


@task(coverage)
def coverage_report(ctx):
    if sys.platform != "win32":
        ctx.run("coverage html", pty=True)
    else:
        ctx.run("coverage html")
