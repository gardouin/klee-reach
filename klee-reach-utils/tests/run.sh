#!/usr/bin/env bash

mkdir -p build
files=$(ls)
for file in $files
do
	name=$(echo $file | sed 's/\.[^.]*$//')
	ext=$(echo $file | sed 's/.*\.//')
	if [ $ext = "ll" ]
	then
		python3 ../kreachdist/main.py $name.ll > a.out
		mv $name.dist build/$name.dist.tmp
		sort -k2 -t: build/$name.dist.tmp > build/$name.dist

		diff build/$name.dist expected/$name.dist.expected > diff.out
		has_diff=$(cat diff.out)
		if [ "$has_diff" = "" ]
		then
			echo "$name.dist: OK"
		else
			echo "$name.dist: ERROR"
		fi
	fi
done

rm -f build/*.dist.tmp a.out diff.out
