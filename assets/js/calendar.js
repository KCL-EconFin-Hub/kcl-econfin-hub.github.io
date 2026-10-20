// Escapes text for an .ics property value (RFC 5545 section 3.3.11).
function icsText(text) {
    return (text || '')
        .trim()
        .replace(/\\/g, '\\\\')
        .replace(/;/g, '\\;')
        .replace(/,/g, '\\,')
        .replace(/\r?\n/g, '\\n');
}

// "2026-11-12" -> "20261112"
function icsDate(date) {
    return date.replace(/-/g, '');
}

// "2026-11-12" -> "2026-11-13"
function nextDay(date) {
    const d = new Date(date + 'T00:00:00Z');
    d.setUTCDate(d.getUTCDate() + 1);
    return d.toISOString().slice(0, 10);
}

// The clock times in free text: "9:30 - 10:45" -> ["093000", "104500"].
function icsTimes(text) {
    return [...(text || '').matchAll(/(\d{1,2}):(\d{2})/g)]
        .map(([, h, m]) => h.padStart(2, '0') + m + '00');
}

// Called with the button's dataset; see _includes/event.html.
//
// If `time` contains a clock time ("14:00-15:00", or "14:00" for one hour)
// the event runs from the start time on `date` to the end time on `endDate`
// (or `date`). Otherwise it is an all-day event spanning `date` to `endDate`.
function downloadCalendar({ title, speaker, date, endDate, time, location, description }) {
    const lastDay = endDate || date;
    const [start, end] = icsTimes(time);
    let when;
    if (start) {
        const oneHourLater = String(Math.min(Number(start.slice(0, 2)) + 1, 23)).padStart(2, '0') + start.slice(2);
        when = [
            `DTSTART:${icsDate(date)}T${start}`,
            `DTEND:${icsDate(lastDay)}T${end || oneHourLater}`
        ];
    } else {
        when = [
            `DTSTART;VALUE=DATE:${icsDate(date)}`,
            `DTEND;VALUE=DATE:${icsDate(nextDay(lastDay))}`
        ];
    }

    const slug = title.replace(/\W+/g, '-').toLowerCase();
    const stamp = new Date().toISOString().replace(/[-:]/g, '').slice(0, 15) + 'Z';
    const details = (speaker ? `Speaker: ${speaker}\n\n` : '') + (description || '');

    const ics = [
        'BEGIN:VCALENDAR',
        'VERSION:2.0',
        'PRODID:-//Economics and Finance Hub//Events//EN',
        'BEGIN:VEVENT',
        `UID:${icsDate(date)}-${slug}@economics-finance-hub`,
        `DTSTAMP:${stamp}`,
        ...when,
        `SUMMARY:${icsText(title)}`,
        `DESCRIPTION:${icsText(details)}`,
        `LOCATION:${icsText(location)}`,
        'END:VEVENT',
        'END:VCALENDAR'
    ].join('\r\n');

    const blob = new Blob([ics], { type: 'text/calendar' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `${slug}.ics`;
    link.click();
}
