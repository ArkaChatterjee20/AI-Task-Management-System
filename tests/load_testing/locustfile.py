
import uuid

from locust import HttpUser, task, between, events
from locust.exception import StopUser


class AI_Task_User(HttpUser):

    wait_time = between(1, 3)

    def on_start(self):
        """Register a dedicated test user and obtain JWT."""

        self.email = f"locust_{uuid.uuid4().hex}@example.com"
        self.password = "LocustTest@123"
        self.task_ids = []

        # Register dedicated test account
        response = self.client.post(
            "/auth/register",
            json={
                "email": self.email,
                "password": self.password,
            },
            name="Register User",
        )

        if response.status_code != 201:
            raise StopUser()

        # Login and obtain JWT
        response = self.client.post(
            "/auth/login",
            json={
                "email": self.email,
                "password": self.password,
            },
            name="Login User",
        )

        if response.status_code != 200:
            raise StopUser()

        token = response.json()["access_token"]

        self.headers = {
            "Authorization": f"Bearer {token}"
        }

    @task(3)
    def create_task(self):
        response = self.client.post(
            "/user-tasks/",
            json={
                "task_title": f"Locust task {uuid.uuid4().hex}"
            },
            headers=self.headers,
            name="Create Task",
        )

        if response.status_code == 201:
            self.task_ids.append(
                response.json()["task_id"]
            )

    @task(4)
    def list_tasks(self):
        self.client.get(
            "/user-tasks/?page=1&page_size=20",
            headers=self.headers,
            name="List Tasks",
        )

    @task(2)
    def retrieve_task(self):
        if not self.task_ids:
            return

        task_id = self.task_ids[-1]

        self.client.get(
            f"/user-tasks/{task_id}",
            headers=self.headers,
            name="Retrieve Task",
        )

    @task(2)
    def update_task(self):
        if not self.task_ids:
            return

        task_id = self.task_ids[-1]

        self.client.patch(
            f"/user-tasks/{task_id}",
            json={
                "is_completed": True
            },
            headers=self.headers,
            name="Update Task",
        )

    @task(1)
    def delete_task(self):
        if not self.task_ids:
            return

        task_id = self.task_ids.pop(0)

        self.client.delete(
            f"/user-tasks/{task_id}",
            headers=self.headers,
            name="Delete Task",
        )

   
