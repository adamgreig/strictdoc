import os
import re

import invoke
from invoke import task


def oneline_command(string):
    return re.sub("\\s+", " ", string).strip()


def run_invoke_cmd(context, cmd):
    return context.run(
        cmd, env=None, hide=False, warn=False, pty=False, echo=True
    )


@task
def clean(context):
    find_command = oneline_command(
        """
        find
            tests
            -type f \\(
                -name '*.script'
            \\)
            -or -type d \\(
                -name '*.dSYM' -or
                -name 'Sandbox' -or
                -name 'Output' -or
                -name 'output'
            \\)
            -not -path "**Expected**"
            -not -path "**Input**"
        """
    )

    find_result = run_invoke_cmd(context, find_command)
    find_result_stdout = find_result.stdout.strip()
    echo_command = oneline_command(
        """echo {find_result} | xargs rm -rfv""".format(
            find_result=find_result_stdout
        )
    )

    run_invoke_cmd(context, echo_command)


@task
def sphinx(context):
    run_invoke_cmd(
        context,
        oneline_command(
            """
            python3 strictdoc/cli/main.py
                export docs
                    --formats=html,rst
                    --output-dir output/sphinx
            """
        ),
    )

    run_invoke_cmd(
        context,
        oneline_command(
            """
            cp -v output/sphinx/rst/strictdoc.rst docs/sphinx/source/ &&
            mkdir -p docs/strictdoc-html/strictdoc-html &&
            cp -rv output/sphinx/html/* docs/strictdoc-html/strictdoc-html
            """
        ),
    )

    run_invoke_cmd(
        context,
        oneline_command(
            """
            cd docs/sphinx &&
                make html latexpdf &&
                open build/latex/strictdoc.pdf
            """
        ),
    )


@task
def test_unit(context):
    command = oneline_command(
        """
        pytest --capture=no
        """
    )

    run_invoke_cmd(context, command)


@task(clean)
def test_integration(context, focus=None, debug=False):
    cwd = os.getcwd()

    strictdoc_exec = 'python \\"{cwd}/strictdoc/cli/main.py\\"'.format(cwd=cwd)

    focus_or_none = "--filter {}".format(focus) if focus else ""
    debug_opts = "-vv --show-all" if debug else ""

    command = oneline_command(
        """
        lit
        --param STRICTDOC_EXEC="{strictdoc_exec}"
        -v
        {debug_opts}
        {focus_or_none}
        {cwd}/tests/integration
        """
    ).format(
        strictdoc_exec=strictdoc_exec,
        cwd=cwd,
        debug_opts=debug_opts,
        focus_or_none=focus_or_none,
    )

    run_invoke_cmd(context, command)


@task
def export_pip_requirements(context):
    run_invoke_cmd(
        context,
        "poetry export --dev --without-hashes --format requirements.txt > requirements.txt",
    )


# Support generation of Poetry managed setup.py file #761
# https://github.com/python-poetry/poetry/issues/761#issuecomment-689491920
@task
def install_local(context):
    command_1 = oneline_command(
        """
        poetry build
        """
    )
    command_2 = oneline_command(
        """
        tar -xvf dist/*.tar.gz --wildcards --no-anchored '*/setup.py' --strip=1
        """
    )
    command_3 = oneline_command(
        """
        pip install -e .
        """
    )

    run_invoke_cmd(context, command_1)
    run_invoke_cmd(context, command_2)
    run_invoke_cmd(context, command_3)


@task
def lint_black_diff(context):
    command = oneline_command(
        """
        black . --color 2>&1
        """
    )
    result = run_invoke_cmd(context, command)

    # black always exits with 0, so we handle the output.
    if "reformatted" in result.stdout:
        print("invoke: black found issues")
        result.exited = 1
        raise invoke.exceptions.UnexpectedExit(result)


@task
def lint_pylint(context):
    command = oneline_command(
        """
        pylint --rcfile=.pylint.ini strictdoc/ tasks.py
        """
    )
    try:
        run_invoke_cmd(context, command)
    except invoke.exceptions.UnexpectedExit as exc:
        # pylink doesn't show an error message when exit code != 0, so we do.
        print(
            "invoke: pylint exited with error code {}".format(exc.result.exited)
        )
        raise exc


@task
def lint_flake8(context):
    command = oneline_command(
        """
        flake8 strictdoc --statistics --max-line-length 80 --show-source
        """
    )
    run_invoke_cmd(context, command)


@task(lint_black_diff, lint_pylint, lint_flake8)
def lint(_):
    pass


@task(lint, test_unit, test_integration)
def test(_):
    pass


# https://github.com/github-changelog-generator/github-changelog-generator
# gem install github_changelog_generator
@task
def changelog(context, github_token):
    command = oneline_command(
        f"""
        github_changelog_generator
        --token {github_token}
        --user strictdoc-project
        --project strictdoc
        """
    )
    run_invoke_cmd(context, command)
