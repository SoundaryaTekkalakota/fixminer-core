#!/bin/bash

# If an argument is given then it is the name of the directory containing the
# files to split.  Otherwise, the files in the working directory are split.
if [ $# -gt 0 ]; then
  dir=$1
else
  dir=.
fi

dest=$2
rm -rf "$dest"
mkdir "$dest"
# The shell glob expands to all the files in the target directory; a different
# glob pattern could be used if you want to restrict splitting to a subset,
# or if you want to include dotfiles.
for file in "$dir"/*; do
  # Details of the split command are up to you.  This one splits each file
  # into pieces named by appending a sequence number to the original file's
  # name.  The original file is left in place.
  lineCount=$(awk 'END {print NR}' $file)
  if [ $lineCount -ne 0 ];then
  	filename="${file##*/}"  
  	more "$file" | tr "\\t" "," > "$dest"/"$filename".csv
  	#split --lines=1000000 --numeric-suffixes "$file" "$file"
  fi
done
