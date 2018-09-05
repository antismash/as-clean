# License: GNU Affero General Public License v3 or later
# A copy of GNU AGPL v3 should have been included in this software package in LICENSE.txt.
"""Clean up old antiSMASH results"""
import argparse
import os
import redis

from . import __version__
from .core import run


def main():
    """Parse the command line, connect to the database, delete old entries"""
    default_db = os.getenv('ASCLEAN_DB', "redis://localhost:6379/0")
    default_workdir = os.getenv('ASCLEAN_WORKDIR', "upload")
    parser = argparse.ArgumentParser()
    parser.add_argument('--db',
            help="URI of the database containing the job queue (default: %(default)s)",
            default=default_db)
    parser.add_argument('-w', '--workdir',
            help="Path to working directory that contains the uploaded sequences (default: %(default)s)",
            default=default_workdir)
    parser.add_argument('--from-db', dest="from_db",
            action="store_true", default=True,
            help="Use the information from the jobs:completed list in Redis")
    parser.add_argument('--from-directory', dest="from_db",
            action="store_false",
            help="Crawl the workdir and do a database lookup based on that")
    parser.add_argument('-n', '--dry-run',
            action="store_true", default=False,
            help="Dry run only, don't change any files or DB entries")
    parser.add_argument('--failed-timeout', type=int, default=7,
            help="Timeout for failed jobs in days (default: %(default)s)")
    parser.add_argument('--done-timeout', type=int, default=30,
            help="Timeout for completed jobs in days (default: %(default)s)")
    options = parser.parse_args()

    redis_store = redis.StrictRedis.from_url(options.db, encoding="utf-8", encoding_errors="ignore", decode_responses=True)
    run(options, redis_store)


if __name__ == "__main__":
    main()
