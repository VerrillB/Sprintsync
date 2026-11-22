"""Post the Jenkins build result to Webex. Called from the Jenkinsfile.

Owner: John Reymond G. Pascual
Usage: python -m sprintsync.notify --status SUCCESS
"""


def main():
    """Read --status, get the commit author, and post the build notice."""
    raise NotImplementedError


if __name__ == "__main__":
    main()
