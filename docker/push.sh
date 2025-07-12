#!/bin/bash
#
# Build image from the currently checked out version of the brainzbot-core
# and push it to the Docker Hub, with an optional tag (by default "latest").
#
# Usage:
#   $ ./push.sh [tag]

cd "$(dirname "${BASH_SOURCE[0]}")/../"

# Save the current git status
git describe --tags --dirty --always > .git-version

TAG_PART=${1:-latest}
docker build --target brainzbot-prod -t metabrainz/brainzbot-core:$TAG_PART \
        --build-arg GIT_COMMIT_SHA=$(git describe --tags --dirty --always) .
docker push metabrainz/brainzbot-core:$TAG_PART
