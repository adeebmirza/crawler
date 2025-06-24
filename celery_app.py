from celery import Celery
# from celery_prometheus_exporter import setup_metrics
# import celery_prometheus_exporter

app = Celery('myapp',
             broker='sqs://',
             backend='mongodb://localhost:27017/celery_results',
             include=['tasks'])  # Use another backend if you prefer (e.g., Redis, database)

# SQS specific settings
app.conf.broker_transport_options = {
    'region': 'us-east-1',  # Change to your AWS region
    'predefined_queues': {
        'myquene': {
            'url': 'https://sqs.us-east-1.amazonaws.com/471112701170/myquene'
        }
    }
}

app.conf.task_default_queue = 'myquene'

# Configure Prometheus metrics
# setup_metrics(app)

# # Expose metrics on port 8888
# celery_prometheus_exporter.start_httpd('0.0.0.0:8888')

# if __name__ == '__main__':
#     app.start()
