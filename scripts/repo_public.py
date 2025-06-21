# Author: Sakthi Santhosh
# Created on: 12/11/2023
import argparse
from os import getenv
from typing import List, Optional

from dotenv import load_dotenv
from requests import get, patch


def list_private_repositories(
    username: str, access_token: str
) -> Optional[dict]:
    url = "https://api.github.com/user/repos?type=private"
    headers = {"Authorization": f"token {access_token}"}

    with get(url, headers=headers, timeout=60) as response:
        if response.status_code == 200:
            return response.json()
        else:
            print(
                f"Error ({response.status_code}): Retreival Failed"
            )
            print("Message:", response.text)
            return None


def make_repositories_public(
    username: str, access_token: str, repo_names: list[str]
) -> None:
    url = f"https://api.github.com/repos/{username}/"
    headers = {
        "Authorization": f"token {access_token}",
        "Accept": "application/vnd.github.v3+json",
    }
    payload = {"private": False}

    for repo_name in repo_names:
        with patch(
            url + repo_name, json=payload, headers=headers, timeout=60
        ) as response:
            if response.status_code == 200:
                print(f'Info: Repository "{repo_name}" | Changed to: Public')
            else:
                print(
                    f"Error ({response.status_code}): Public-ization Failed: "
                    f'"{repo_name}"'
                )
                print("Message:", response.text)


def read_repo_names_from_file(filename: str) -> List[str]:
    try:
        with open(filename, "r") as file:
            repo_names = [line.strip() for line in file if line.strip()]
        return repo_names
    except FileNotFoundError:
        print(f'Error: Not Found: File "{filename}"')
        return []


def main() -> None:
    load_dotenv(dotenv_path=".env.local")

    parser = argparse.ArgumentParser(
        description="GitHub Repositories Public-izer"
    )
    parser.add_argument(
        "-f",
        "--file",
        help="file containing repository names to make public (one per line)",
        type=str,
    )
    args = parser.parse_args()

    username = getenv("GITHUB_USERNAME", "")
    access_token = getenv("GITHUB_ACCESS_TOKEN", "")

    if args.file:
        repo_names = read_repo_names_from_file(args.file)
        if repo_names:
            make_repositories_public(username, access_token, repo_names)
        else:
            print("Noting to Process")
    else:
        confirm = input(
            "Continue? (yes/no): "
        )
        if confirm.lower() != "yes":
            print("Exiting...")
            return

        private_repositories = list_private_repositories(
            username, access_token
        )
        if private_repositories:
            repo_names = [
                repository["name"] for repository in private_repositories
            ]
            make_repositories_public(username, access_token, repo_names)


if __name__ == "__main__":
    main()
