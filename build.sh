#!/usr/bin/env bash
# Push to dockerdex: https://dockerdex.umcn.nl
# Run: docker login dockerdex.umcn.nl:5005 first (PAT with read_registry, write_registry)

REGISTRY="dockerdex.umcn.nl:5005"
USER_OR_GROUP="${USER_OR_GROUP:-nielsrocholl}"  # set to your GitLab username or group
PROJECT="nnunetv2"
TAG="${TAG:-latest}"

docker build --tag "${REGISTRY}/${USER_OR_GROUP}/${PROJECT}:${TAG}" .
docker push "${REGISTRY}/${USER_OR_GROUP}/${PROJECT}:${TAG}"
