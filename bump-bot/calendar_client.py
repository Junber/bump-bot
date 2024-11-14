import datetime
import json
import os
import caldav

import bump_bot_config as config


def get_event_summary(happening_in_person: bool):
    if happening_in_person:
        return config.get_default_calendar_event_summary()
    else:
        return config.get_in_person_calendar_event_summary()


class Calendar:
    valid = False
    client: caldav.DAVClient
    calendar: caldav.Calendar

    def __init__(self) -> None:
        if not os.path.exists("config/calendar.json"):
            return

        cal_config = {}
        with open("config/calendar.json", "r", encoding="utf-8") as config_file:
            cal_config = json.loads(config_file.read())

        try:
            self.client = caldav.DAVClient(
                url=cal_config["url"],
                username=cal_config["username"],
                password=cal_config["password"],
            )
            self.calendar = self.client.principal().calendars()[0]
            self.valid = True
        except:
            pass

    def find_events(self, date: datetime.date) -> list[caldav.CalendarObjectResource]:
        if not self.valid:
            return []

        return self.calendar.search(
            start=date,
            end=date + datetime.timedelta(1),
            event=True,
        )

    def delete_events(self, date: datetime.date) -> None:
        if not self.valid:
            return

        for event in self.find_events(date):
            event.delete()

    def create_event(
        self, date: datetime.date, time: datetime.time | None, happening_in_person: bool
    ) -> bool:
        if not self.valid:
            return True

        start_time = None
        if time:
            start_time = datetime.datetime.combine(date, time)

        summary = get_event_summary(happening_in_person)

        for event in self.find_events(date):
            calendar_time = event.icalendar_component["dtstart"].dt  # type: ignore
            if (
                isinstance(calendar_time, datetime.datetime)
                and isinstance(start_time, datetime.datetime)
                and calendar_time.astimezone() == start_time.astimezone()
                and event.icalendar_component["summary"] == summary  # type: ignore
            ):
                return False
            event.delete()

        if time:
            self.calendar.save_event(
                dtstart=start_time,
                dtend=datetime.datetime.combine(date, datetime.time(23, 59, 59)),
                summary=summary,
            )
        else:
            self.calendar.save_event(
                dtstart=date,
                summary=summary,
            )
        return True


calendar = Calendar()
