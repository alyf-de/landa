import google.auth.transport.requests
import requests
from google.oauth2 import service_account
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential


class FirebaseNotification:
	def __init__(self, cert, project_id):
		self.cert = cert
		self.url = f"https://fcm.googleapis.com/v1/projects/{project_id}/messages:send"
		self.token = self._get_access_token()

	def _get_access_token(self) -> str:
		"""Retrieve a valid access token to authorize requests.

		:return: Access token.
		"""
		credentials = service_account.Credentials.from_service_account_file(
			self.cert,
			scopes=[
				"https://www.googleapis.com/auth/cloud-platform",
				"https://www.googleapis.com/auth/firebase",
			],
		)
		request = google.auth.transport.requests.Request()
		credentials.refresh(request)
		return credentials.token

	@property
	def headers(self):
		"""Get headers for authorized requests."""
		return {
			"Authorization": f"Bearer {self.token}",
		}

	def send_to_topic(self, topic: str, data: dict = None) -> requests.Response:
		"""Send a message to a topic."""
		return self.send_request(data={"topic": topic, "data": data})

	def send_to_token(self, token: str, data: dict = None) -> requests.Response:
		"""Send a message to a token."""
		return self.send_request(data={"token": token, "data": data})

	@retry(
		retry=retry_if_exception_type(requests.RequestException),
		stop=stop_after_attempt(3),
		wait=wait_exponential(multiplier=1, min=4, max=10),
	)
	def send_request(self, data: dict) -> requests.Response:
		"""Send a POST request."""
		response = requests.post(self.url, headers=self.headers, json={"message": data})
		response.raise_for_status()
		return response
