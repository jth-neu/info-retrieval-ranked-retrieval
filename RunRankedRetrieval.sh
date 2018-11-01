#!/usr/bin/env bash
if [ "$1" != "" ] && [ "$2" != "" ] && [ "$3" != "" ] && [ $4 -gt 0 ]
then
	python3 ranked_retrieval.py "$1" "$2" "$3" $4
else
	echo Invalid input.
fi