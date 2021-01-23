#!/usr/bin/env bash

set -e

init_flag='false'

print_usage() {
    printf "Usage: repo_setup [-i] [-d <dir>]\n"
    printf "\t-i \t\t First init of the repo (after creation)\n"
}

while getopts 'id:sh' flag; do
    case "${flag}" in
        i)  init_flag='true';;
        h)  print_usage
            exit 0;;
        *)  print_usage
            exit 1 ;;
    esac
done


# Install git lfs
git lfs install

# Unset -e
set +e

# Set conda environment
conda env update -f environment.yml

if [[ "$init_flag" = "true" ]]; then
    # Set remote url to expected default
    git init
    git remote add origin https://github.com/kenanozturk/autopilot-map.git
    git add README.md
    git commit -m "Add readme" README.md
    git push --set-upstream origin master
    git checkout -b develop

    # Push to upstream develop
    git add *
    git commit -m "Initial setup commit"
    git push --set-upstream origin develop
fi
