# Make sure we start from scratch
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
