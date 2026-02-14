---
icon: lucide/git-pull-request-arrow
---

# Contributing

This page will teach you how to contribute to this repository.

## Clone the repository

The first thing you must do is clone the repository. This puts the project code onto your machine.

To "clone" this repository, complete the following steps:

1. Fork the GitHub repository. See [GitHub's official guide](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/fork-a-repo) for more information!
2. Clone your branch to your machine.

    ```bash
    $ git clone https://github.com/<your_username>/TERMINALCASINO.git
    ```

3. Create a branch. The branch name should describe what you want to add or fix.

    ```bash
    $ git branch <branch-name>
    $ git checkout <branch-name>
    ```

That's it! Now, you can begin making changes to the repository.

## Merge changes

Once you have finished making your changes to the repository, you will want to "merge" your changes with the main repo. This ensures your changes are refected in the repository.

To merge changes, complete the following:

1. On your machine, merge your branch's changes with your `main` branch.

    ```bash
    $ git checkout main
    $ git merge <your-branch>
    ```

2. Go to [TERMINALCASINO's pull requests](https://github.com/ufosc/TERMINALCASINO/pulls) and [open a pull request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request).
3. If needed, resolve any merge conflicts. If you have any issues merging conflicts, please let the project maintainers know.

