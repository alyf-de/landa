import json

import google.auth.transport.requests
import requests
from google.oauth2 import service_account


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
			"Content-Type": "application/json; UTF-8",
		}

	def send_to_topic(self, topic: str, data: dict = None) -> requests.Response:
		"""Send a message to a topic."""
		return requests.post(
			self.url,
			headers=self.headers,
			data=json.dumps(
				{
					"message": {
						"topic": topic,
						"data": data,
					}
				}
			),
		)

	def send_to_token(self, token: str, data: dict = None) -> requests.Response:
		"""Send a message to a token."""
		return requests.post(
			self.url,
			headers=self.headers,
			data=json.dumps(
				{
					"message": {
						"token": token,
						"data": data,
					}
				}
			),
		)
