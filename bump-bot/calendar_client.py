import datetime
import json
import os
import caldav

import bump_bot_config as config


class Calendar:
    valid = False
    client: caldav.DAVClient
    calendar: caldav.Calendar

    def __init__(self) -> None:
        if not os.path.exists("config/calendar.json"):
            return

        self.valid = True
        cal_config = {}
        with open("config/calendar.json", "r", encoding="utf-8") as config_file:
            cal_config = json.loads(config_file.read())

        self.client = caldav.DAVClient(
            url=cal_config["url"], username=cal_config["username"], password=cal_config["password"]
        )
        self.calendar = self.client.principal().calendars()[0]

    def find_events(self, date: datetime.date) -> list[caldav.CalendarObjectResource]:
        return self.calendar.search(
            start=date,
            end=date + datetime.timedelta(1),
            summary=config.get_calendar_event_summary(),
            event=True,
        )

    def create_event(self, date: datetime.date, time: datetime.time | None) -> bool:
        start_time = None
        if time:
            start_time = datetime.datetime.combine(date, time)
        for event in self.find_events(date):
            calendar_time = event.icalendar_component["dtstart"].dt  # type: ignore
            if (
                calendar_time is datetime.datetime
                and start_time is datetime.datetime
                and calendar_time.astimezone() == start_time.astimezone()
            ):
                return False
            event.delete()
        if time:
            self.calendar.save_event(
                dtstart=start_time,
                dtend=datetime.datetime.combine(date, datetime.time(23, 59, 59)),
                summary=config.get_calendar_event_summary(),
            )
        else:
            self.calendar.save_event(
                dtstart=date,
                summary=config.get_calendar_event_summary(),
            )
        return True


calendar = Calendar()
