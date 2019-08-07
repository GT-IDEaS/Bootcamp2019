GitHub Flow Instructions
========================

1. Make sure you're up-to-date with `upstream:master`
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
5. Open a pull request to `upstream:master` from your fork (`origin`)
6. Wait on PR comments, suggestions, etc. and re-edit your code
7. Success!

**Note: After making changes to a file, make sure to add & commit your changes _before_
attempting to pull with rebase (step 1 above)!**
