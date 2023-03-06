# [R]ecursively [Git]

`git` operate on all projects under a specific GitLab group, powered by GraphQL

## How it works

1. Using GraphQL, it retrieves all the projects in the GitLab group
2. `git clone` all the project in the provided root folder
3. `git fetch` all projects if it was previously clone

## How to use

```shell
# Create a virtualenv
python3 -m venv venv
# Active the virtual env
. venv/bin/activate
# Install related dependencies
pip3 install -r requirements.txt

# URL   : GitLab's GraphQL endpoint
# AUTH  : GitLab's [personal access token](https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html)
# GROUP : GitLab group to start from
# ROOT  : The root folder where to clone all the repository
URL=https://gitlab.com/api/graphql AUTH=<access token> GROUP=gitlab-org ROOT=/Users/userA/Workspace python3 main.py
```