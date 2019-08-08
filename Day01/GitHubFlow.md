GitHub Flow Instructions
========================

> **Note: After making changes to a file, make sure to add & commit your
> changes (steps 2-3) _before_ attempting to pull with rebase!**

To update your local machine & remote fork (`origin`):
1. Make sure your local machine is up-to-date with `upstream:master`
    ```
    > git pull --rebase upstream master
    ```
2. Make some changes to `file1` locally
3. Add & commit your changes locally
    ```
    > git add file1
    > git commit -m "Changes to file1"
    ```
4. Push your commits to your `origin:master`
    ```
    > git push --force origin master
    ```

If you're interested in contributing your changes back into the `upstream`
repository:
1. Open a pull request to `upstream:master` from your fork (`origin`)
2. Wait on PR comments, suggestions, etc. and re-edit your code
3. Add, commit, and push your changes to `origin`. GitHub will automatically
incorporate these changes into your pull request!



