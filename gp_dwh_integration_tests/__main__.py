from gp_dwh_integration_tests.app import app
from gp_dwh_integration_tests.cli import cli


def main():
    return cli(app)


if __name__ == '__main__':
    main()
