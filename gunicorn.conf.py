bind = "0.0.0.0:80"
accesslog = '-'
errorlog = '-'
workers = '2'
worker_tmp_id = '/dev/shm'
worker_class = 'uvicorn.workers.UvicornWorker'