"""Console script for mosayc."""
import sys
import click


@click.command()
@click.version_option(message="Mosayc, version %(version)s")
def main(args=None):
    """Console script for mosayc."""
    click.echo("Replace this message by putting your code into "
               "mosayc.cli.main")
    click.echo("See click documentation at https://click.palletsprojects.com/")
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
