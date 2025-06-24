from celery_app import app

# Construct the message body as a single dictionary
message_body = {
    'post_id': '6857db8724ba654327dbf68d',
    'text': 'Russia is a country located in Eastern Europe and Northern Asia.?',
}

# Send the task with one argument: message_body
result = app.send_task(
    'process_message',
    args=[message_body]
)

print(f"Task sent with ID: {result.id}")
