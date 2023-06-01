import gitlab
from .version import __version__

def generate_release_notes(project_id, endstr = '  <br>', **config):
    """
    Generate the release notes of a gitlab project from the last release

    Parameters
    ----------
    project_id: int
        ID of the project
    config: dict
        url: Optional[str] = None,
        private_token: Optional[str] = None,
        oauth_token: Optional[str] = None,
        job_token: Optional[str] = None,
        ssl_verify: Union[bool, str] = True,
        http_username: Optional[str] = None,
        http_password: Optional[str] = None,
        timeout: Optional[float] = None,
        api_version: str = '4',
        session: Optional[requests.sessions.Session] = None,
        per_page: Optional[int] = None,
        pagination: Optional[str] = None,
        order_by: Optional[str] = None,
        user_agent: str = 'python-gitlab/3.1.0',
        retry_transient_errors: bool = False,
    """

    gl = gitlab.Gitlab(**config)
    project = gl.projects.get(project_id)

    if not project.mergerequests.list(state='merged'):
        raise ValueError(f"There is not merged merge request for project {project_id} {project.name}")

    if not project.releases.list():
        log = f"Changelog of {project.name}:{endstr}"
        last_date = '0000-01-01T00:00:00Z'
    else:
        last_release = project.releases.list()[0]
        log = f"Changelog since release {last_release.name} of {project.name}:{endstr}"
        last_date = last_release.released_at

    page = 1
    list_mrs = project.mergerequests.list(state='merged',
                                          order_by='updated_at',
                                          updated_after=last_date,
                                          page=page)
    if not list_mrs:
        log += f"There is no merged merge request after {last_date}"
        return log

    while list_mrs:
        for mr in list_mrs:
            line = f" * {mr.title} (@{mr.author['username']}){endstr}"
            log += line

        page += 1
        list_mrs = project.mergerequests.list(state='merged',
                                              order_by='updated_at',
                                              updated_after=last_date,
                                              page=page
                                              )

    return log


def main():
    import argparse
    parser = argparse.ArgumentParser("Generate release notes for a gitlab repository \
                                    based on merge requests titles since last release")

    # Required
    parser.add_argument("project_id", type=int)
    # Optional
    parser.add_argument("--url", default="https://gitlab.com", required=False)
    parser.add_argument("--private_token", type=str, required=False, default=None)
    parser.add_argument('--version', action='version', version=__version__)
    parser.add_argument('--html', action='store_true')

    args = parser.parse_args()

    if args.html:
        endstr = '  <br>'
    else:
        endstr = '\n'
    notes = generate_release_notes(args.project_id, url=args.url, endstr=endstr, private_token=args.private_token)
    print(notes)


if __name__ == "__main__":
    main()
