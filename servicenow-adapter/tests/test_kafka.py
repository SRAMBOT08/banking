from app.config.settings import AdapterSettings
from app.events.kafka import AdapterEventPublisher


class FakeProducer:
    def __init__(self):
        self.items = []

    def produce(self, topic, key=None, value=None):
        self.items.append((topic, key, value))

    def poll(self, _timeout):
        return None

    def flush(self, _timeout):
        return None


def test_kafka_publisher_uses_only_required_topics():
    settings = AdapterSettings(SERVICENOW_USERNAME="user", SERVICENOW_PASSWORD="pass")
    publisher = AdapterEventPublisher(settings)
    publisher.producer = FakeProducer()
    publisher.publish_started({"x": 1}, "k")
    publisher.publish_completed({"x": 1}, "k")
    publisher.publish_failed({"x": 1}, "k")
    publisher.publish_verified({"x": 1}, "k")
    topics = [item[0] for item in publisher.producer.items]
    assert topics == [
        settings.execution_started_topic,
        settings.execution_completed_topic,
        settings.execution_failed_topic,
        settings.execution_verified_topic,
    ]
