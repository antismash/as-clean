from datetime import datetime, timedelta
import glob
from os import path
from shutil import rmtree


from antismash_models.job import SyncJob as Job


def run(options, redis_store):
    """Run the cleanup process"""
    if options.from_db:
        from_db(options, redis_store)
    else:
        from_dir(options, redis_store)


def from_db(options, redis_store):
    """Run the cleanup based on info from the database"""
    counter = 0
    jobs = redis_store.lrange('jobs:completed', 0, -1)[::-1]
    for job_id in jobs:
        job = Job(redis_store, job_id).fetch()

        if should_remove_job(options, job):
            remove_job(options, redis_store, job)
            counter += 1
            continue

        if job.state == 'removed':
            dirname = path.join(options.workdir, job.job_id)
            remove_stale_dir(options, dirname)
    print("Removed", counter, "jobs")


def from_dir(options, redis_store):
    """Run the cleanup by crawling the work dir and doing database lookups based on that"""
    dirs_to_check = glob.glob(path.join(options.workdir, '*-*-*'))
    for dirname in dirs_to_check:
        dir_id = path.basename(dirname)
        job_key = u'job:{}'.format(dir_id)
        if not redis_store.exists(job_key):
            print("Can't find job {}, removing stale dir".format(dir_id))
            remove_stale_dir(options, dirname)
            continue
        job = Job(redis_store, dir_id).fetch()
        if should_remove_job(options, job):
            remove_job(options, redis_store, job)
            continue
        print("Not removing job ", job.uid)


def should_remove_job(options, job):
    """check if jobs should be removed"""
    failed_timeout = timedelta(days=options.failed_timeout)
    done_timeout = timedelta(days=options.done_timeout)
    now = datetime.utcnow()

    if job.state in ('running', 'pending'):
        return False
    if job.state == 'done':
        if now - job.last_changed < done_timeout:
            return False
        return True
    if job.state == 'failed':
        if now - job.last_changed < failed_timeout:
            return False
        return True

    return False


def remove_job(options, redis_store, job):
    """Remove a job's working directory and set the job status to removed"""
    print("Removing job {} ending with status {!r} on {}".format(job.job_id, job.state, job.last_changed))
    if not options.dry_run:
        rmtree(path.join(options.workdir, job.job_id), ignore_errors=True)
        job.status = "removed: {}: {}".format(job.state, job.status)
        job.state = "removed"
        job.commit()
        redis_store.lrem('jobs:completed', 0, job.job_id)
        redis_store.lpush('jobs:removed', job.job_id)


def remove_stale_dir(options, dirname):
    """Remove a stale job directory"""
    if path.exists(dirname):
        print("Removing stale directory for job {}".format(dirname))
        if not options.dry_run:
            rmtree(dirname)
