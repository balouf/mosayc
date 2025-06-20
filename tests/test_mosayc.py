#!/usr/bin/env python

"""Tests for `mosayc` package."""

import pytest
from click.testing import CliRunner
import os

from mosayc import cli


@pytest.fixture
def response():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    # import requests
    # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')


def test_content(response):
    """Sample pytest test function with the pytest fixture as an argument."""
    # from bs4 import BeautifulSoup
    # assert 'GitHub' in BeautifulSoup(response.content).title.string


def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()
    result = runner.invoke(
        cli.main, ["-R", os.path.join(os.getcwd(), "example"), "-Q", 1, "-S", 1]
    )
    assert result.exit_code == 0
    assert "Mosaic saved" in result.output
    help_result = runner.invoke(cli.main, ["--help"])
    assert help_result.exit_code == 0
    assert "Console script for mosayc." in help_result.output
