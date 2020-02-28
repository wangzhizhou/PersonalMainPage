# !/usr/bin/env bash
# -*- coding: utf-8 -*-

if [ "`git status -s`" ]
then
    echo "The working directory is dirty. Please commit any pending changes."
    exit 1;
fi

SITE_ROOT="Orz"
SITE_PUB_DIR="${SITE_ROOT}/public"
SITE_CONTENT_DIR="${SITE_ROOT}/content"
SITE_THEME_DIR="${SITE_ROOT}/themes"

echo "Deleting old publication"
rm -rf ${SITE_PUB_DIR}
<<<<<<< HEAD
=======
mkdir ${SITE_PUB_DIR}
>>>>>>> 3f0eb83e52594b3b8f085f2dccde63a904d0e69f
git worktree prune
rm -rf .git/worktrees/${SITE_PUB_DIR}

echo "Checking out gh-pages branch into public"
<<<<<<< HEAD
git worktree add ${SITE_PUB_DIR} -B gh-pages origin/gh-pages
=======
git worktree add -B gh-pages ${SITE_PUB_DIR} origin/gh-pages
>>>>>>> 3f0eb83e52594b3b8f085f2dccde63a904d0e69f

echo "Removing existing files"
rm -rf ${SITE_PUB_DIR}/*

echo "$base_url" > ${SITE_PUB_DIR}/CNAME

echo "Generating site"
hugo -s "${SITE_ROOT}" -e production

echo "Updating gh-pages branch"
<<<<<<< HEAD
cd ${SITE_PUB_DIR} && echo "$base_url" > ${SITE_PUB_DIR}/CNAME && git add --all && git commit -m "Publishing to gh-pages (publish.sh)"
=======
cd ${SITE_PUB_DIR} && git add --all && git commit -m "Publishing to gh-pages (publish.sh)"
>>>>>>> 3f0eb83e52594b3b8f085f2dccde63a904d0e69f

echo "Pushing to github"
cd - 
git push --all
open "http://$base_url"

