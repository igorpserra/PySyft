docker ps --format '{{.Names}}' | grep "celeryworker" |  xargs -I '{}' bash -c 'echo "{} -> $(docker exec -i {} bash < input.sh) "' - {}