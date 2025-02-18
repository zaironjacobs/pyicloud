"""Reminders service."""
from datetime import datetime
import time
import uuid
import json


class RemindersService:
    """The 'Reminders' iCloud service."""

    def __init__(self, service_root, session, params):
        self.session = session
        self._params = params
        self._service_root = service_root

        self.lists = {}
        self.collections = {}

        self.refresh()

    def refresh(self):
        """Refresh data."""
        params_reminders = dict(self._params)
        params_reminders.update(
            {"clientVersion": "4.0", "lang": "en-us", "usertz": 'UTC'}
        )

        # Open reminders
        req = self.session.get(
            self._service_root + "/rd/startup", params=params_reminders
        )

        data = req.json()

        self.lists = {}
        self.collections = {}
        for collection in data.get("Collections"):
            temp = []
            self.collections[collection.get("title")] = {
                "guid": collection.get("guid"),
                "ctag": collection.get("ctag"),
            }
            for reminder in data.get("Reminders"):

                if reminder.get("pGuid") != collection.get("guid"):
                    continue

                if reminder.get("dueDate"):
                    due = datetime(
                        reminder.get("dueDate")[1],
                        reminder.get("dueDate")[2],
                        reminder.get("dueDate")[3],
                        reminder.get("dueDate")[4],
                        reminder.get("dueDate")[5],
                    )
                else:
                    due = None

                if reminder.get('priority'):
                    prio = reminder.get('priority')
                else:
                    prio = 0

                if reminder.get('description'):
                    desc = reminder.get('description')
                else:
                    desc = ''

                temp.append(
                    {
                        "title": reminder.get("title"),
                        "desc": desc,
                        "due": due,
                        "guid": reminder.get('guid'),
                        "priority": prio
                    }
                )
            self.lists[collection.get("title")] = temp

    def post(self, time_zone, title, description="", collection=None, due_date=None):
        """Adds a new reminder."""
        pguid = "tasks"
        if collection:
            if collection in self.collections:
                pguid = self.collections[collection]["guid"]

        params_reminders = dict(self._params)
        params_reminders.update(
            {"clientVersion": "4.0", "lang": "en-us", "usertz": time_zone}
        )

        due_dates = None
        if due_date:
            due_dates = [
                int(str(due_date.year) + str(due_date.month) + str(due_date.day)),
                due_date.year,
                due_date.month,
                due_date.day,
                due_date.hour,
                due_date.minute,
            ]

        req = self.session.post(
            self._service_root + "/rd/reminders/tasks",
            data=json.dumps(
                {
                    "Reminders": {
                        "title": title,
                        "description": description,
                        "pGuid": pguid,
                        "etag": None,
                        "order": None,
                        "priority": 0,
                        "recurrence": None,
                        "alarms": [],
                        "startDate": None,
                        "startDateTz": None,
                        "startDateIsAllDay": False,
                        "completedDate": None,
                        "dueDate": due_dates,
                        "dueDateIsAllDay": False,
                        "lastModifiedDate": None,
                        "createdDate": None,
                        "isFamily": None,
                        "createdDateExtended": int(time.time() * 1000),
                        "guid": str(uuid.uuid4()),
                    },
                    "ClientState": {"Collections": list(self.collections.values())},
                }
            ),
            params=params_reminders,
        )
        return req.ok
