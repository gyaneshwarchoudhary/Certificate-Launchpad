from abc import ABC, abstractmethod

class BaseMailer(ABC):
    @abstractmethod
    def send_email(self, receiver: str, subject: str, body: str, attachment_path: str) -> bool:
        """Send an email with attachment."""
        pass
