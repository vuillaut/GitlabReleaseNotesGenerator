import datetime
import dateutil.parser  
import gitlab
import os.path
import sys
from .version import __version__

def generate_release_notes(project_id, endstr = '  <br>', since=None, quiet=False, **config):
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

    if not project.mergerequests.list(get_all=False,state='merged'):
        raise ValueError(f"There is no merged merge request for project {project_id} {project.name}")

    log = ""

    if since:
        log_pending = f"Changelog of {project.name} since {since}:{endstr}"
        last_date = since
    elif not project.releases.list(get_all=False):
        log_pending = f"Changelog of {project.name}:{endstr}"
        last_date = dateutil.parser.isoparse('0000-01-01T00:00:00Z')
    else:
        last_release = project.releases.list(get_all=False)[0]
        log_pending = f"Changelog since release {last_release.name} of {project.name}:{endstr}"
        last_date = dateutil.parser.isoparse(last_release.released_at)

    last_datetime = last_date
    if not isinstance(last_datetime, datetime.datetime):
        last_datetime = \
            datetime.datetime.combine(last_datetime, datetime.datetime.min.time()) \
                .replace(tzinfo=datetime.timezone.utc)

    page = 1
    list_mrs = project.mergerequests.list(state='merged',
                                          get_all=False,
                                          order_by='merged_at',
                                          updated_after=last_date,
                                          page=page)
    if not list_mrs:
        if not quiet:
            log += log_pending
            log += f"There is no merged merge request after {last_date}{endstr}"
        return log

    log += log_pending
    while list_mrs:
        for mr in list_mrs:
            # `updated_at` could be after `merged_at`, e.g. for MRs that has
            # additional comments after it's merged.
            if dateutil.parser.isoparse(mr.merged_at) < last_datetime:
                continue

            line = f" * {mr.title} (@{mr.author['username']}){endstr}"
            log += line

        page += 1
        list_mrs = project.mergerequests.list(state='merged',
                                              get_all=False,
                                              order_by='updated_at',
                                              updated_after=last_date,
                                              page=page
                                              )

    return log


def main():
    import argparse
    parser = argparse.ArgumentParser(os.path.basename(sys.argv[0]),
                                     description="Generate release notes for a gitlab repository \
                                     based on merge requests titles since last release")

    # Required
    parser.add_argument("project_id", type=int)
    # Optional
    parser.add_argument("--url", default="https://gitlab.com", required=False)
    parser.add_argument("--private_token", type=str, required=False, default=None)
    parser.add_argument('--version', action='version', version=__version__)
    parser.add_argument('--html', action='store_true')
    parser.add_argument('--since', type=datetime.date.fromisoformat, required=False, default=None)
    parser.add_argument('--quiet', action='store_true')

    args = parser.parse_args()

    if args.html:
        endstr = '  <br>'
    else:
        endstr = '\n'
    notes = generate_release_notes(args.project_id,
                                   url=args.url,
                                   endstr=endstr,
                                   since=args.since,
                                   quiet=args.quiet,
                                   private_token=args.private_token,
            )
    if notes:
        print(notes)

if __name__ == "__main__":
    main()
