## MyGit

This is a simple and naive implementation of git for educational purposes. To simplify the implementation more, json format is used to store the files instead of binary format. This removes the need to work with bytes directly.

## Install

Run the following command in terminal
```
source ./install.sh
```

## Example
After install, we can use mygit instead of git.
Please see test folder for example.

```
# Make sure we start from scratch
mkdir test
cd test
rm -rf .mygit *.txt

# Generate some files
echo "1111" > 1.txt
echo "2222" > 2.txt

# Init
mygit init ./

# Add the files
mygit add ./

# 1st Commit
mygit commit -a "EasyPeasy" -m "1st commit"

# Get status
# mygit status

# Make some changes to file 1.txt
echo "0000" > 1.txt

# Stage the files
mygit add ./

# 2nd Commit
mygit commit -a "Mistake Maker" -m "2nd commit"

# Get logs
mygit log

# Checkout the first commit
# mygit checkout 

# Check the file 1.txt
cat 1.txt

```

## References

https://git-scm.com/docs/

https://wyag.thb.lt/

http://gitlet.maryrosecook.com/docs/gitlet.html

https://benhoyt.com/writings/pygit/

https://www.leshenko.net/p/ugit
