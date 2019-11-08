import datetime


class HumanReadable:

    def EclapsedTime(self, created_at=None):
        created_at = created_at or datetime.datetime.now()
        current_time = datetime.datetime.now(datetime.timezone.utc)
        timediff = current_time - created_at
        readable_time = {'days': 0, 'hours': 0, 'minutes': 0, 'seconds': 0}
        readable_time['seconds'] = timediff.seconds % 60

        minutes = int(timediff.seconds / 60)
        readable_time['minutes'] = minutes % 60

        hours = int(minutes / 60)
        readable_time['hours'] = hours % 24

        readable_time['days'] = timediff.days

        readableString = ''
        if readable_time['days']:
            if readable_time['days'] == 1:
                readableString += f"{readable_time['days']} Day and "
            else:
                readableString += f"{readable_time['days']} Days and "
        if readable_time['hours']:
            readableString += f"{readable_time['hours']}h:"
        if readable_time['minutes']:
            readableString += f"{readable_time['minutes']}m:"
        if readable_time['seconds']:
            readableString += f"{readable_time['seconds']}s"

        return readableString
