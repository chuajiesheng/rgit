import os
from dataclasses import dataclass, field
from pprint import pprint
from typing import List

from git import Repo
from git.exc import InvalidGitRepositoryError, NoSuchPathError
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport

QUERY = gql("""
    query ($path: ID!) {
        group(fullPath: $path) {
            descendantGroups {
                nodes {
                    fullName
                    fullPath
                    projects {
                        nodes {
                            name
                            fullPath
                            httpUrlToRepo
                        }
                    }
                }
            }
            fullName
            fullPath
            projects {
                nodes {
                    name
                    fullPath
                    httpUrlToRepo
                }
            }
        }
    }
    """)


@dataclass
class Project:
    name: str
    full_path: str
    git_path: str


@dataclass
class Group:
    name: str
    full_path: str
    projects: List[Project] = field(default_factory=list)

    def add_projects(self, projects):
        print(f"## {self.name}")
        for p in projects.get('nodes'):
            self.projects.append(Project(p.get('name'), p.get('fullPath'), p.get('httpUrlToRepo')))


def _check_current_user(c):
    query = gql('query {currentUser {name}}')
    result = c.execute(query)
    pprint(result)


def _check_groups(c, group):
    params = {'path': group}
    r = c.execute(QUERY, variable_values=params).get('group')

    root_group = Group(r.get('fullName'), r.get('fullPath'))
    root_group.add_projects(r.get('projects'))

    groups = [root_group]
    for g in r.get('descendantGroups').get('nodes'):
        group = Group(g.get('fullName'), g.get('fullPath'))
        pprint(g)
        group.add_projects(g.get('projects'))
        groups.append(group)

    return groups


def _process_group(group):
    print(f"## {g.name}")

    for p in group.projects:
        _process_project(p)


def _process_project(project):
    print(f"### {project.name}")
    repo_dir = os.path.join(root_path, project.full_path)
    try:
        repo = Repo(repo_dir)
        git = repo.git
        git.fetch('--all')
    except (InvalidGitRepositoryError, NoSuchPathError):
        os.makedirs(repo_dir, exist_ok=True)
        Repo.clone_from(project.git_path, repo_dir)


if __name__ == '__main__':
    url = os.environ.get('URL') if 'URL' in os.environ else input('GitLab GraphQL URL: ')
    auth = os.environ.get('AUTH') if 'AUTH' in os.environ else input('GitLab Access Token: ')
    group = os.environ.get('GROUP') if 'GROUP' in os.environ else input('Group: ')
    root_path = os.environ.get('ROOT') if 'ROOT' in os.environ else input('Root Path: ')

    HEADERS = {'Authorization': f"Bearer {auth}"}
    transport = AIOHTTPTransport(url=url, headers=HEADERS)

    client = Client(transport=transport, fetch_schema_from_transport=True)
    print('# Current User')
    _check_current_user(client)

    print('# Groups')

    for g in _check_groups(client, group):
        _process_group(g)