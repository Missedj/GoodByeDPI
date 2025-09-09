from redis import Redis
from rq import Worker, Queue, Connection
from common.config import settings
def main():
    redis = Redis.from_url(settings.redis_url)
    with Connection(redis):
        worker = Worker(map(Queue, ["jobs"]))
        worker.work(with_scheduler=True)
if __name__ == "__main__":
    main()
