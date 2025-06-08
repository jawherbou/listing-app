#!/bin/sh

set -e

host="$1"
shift
cmd="$@"

echo "Waiting for PostgreSQL at $host to be ready..."

until pg_isready -h "$host" -p 5432 > /dev/null 2>&1; do
  sleep 1
done

echo "PostgreSQL is up."
exec $cmd