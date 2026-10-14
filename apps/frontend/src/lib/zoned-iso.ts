/** Interpret the Scheduling Service's institution-local civil time in its IANA zone.
 * Unlike `${date}T${time}`, the returned ISO instant is independent of browser timezone.
 */
export function zonedInstant(date: string, time: string, timezone: string): string {
  if (!date || !time || time.includes("T")) return time;
  if (!/^\d{4}-\d{2}-\d{2}$/.test(date) || !/^\d{2}:\d{2}/.test(time)) return `${date}T${time}`;
  const [y, m, d] = date.split("-").map(Number) as [number, number, number];
  const [h, min, sec] = time.split(":").map(Number) as [number, number, number?];
  const reference = Date.UTC(y, m - 1, d, h, min, sec || 0);
  const formatter = new Intl.DateTimeFormat("en-GB", {
    timeZone: timezone, year: "numeric", month: "2-digit", day: "2-digit",
    hour: "2-digit", minute: "2-digit", second: "2-digit", hourCycle: "h23"
  });
  function localClockAsUtc(instant: number) {
    const parts = Object.fromEntries(formatter.formatToParts(new Date(instant)).map(p => [p.type, p.value]));
    return Date.UTC(Number(parts.year), Number(parts.month) - 1, Number(parts.day),
      Number(parts.hour), Number(parts.minute), Number(parts.second));
  }
  let instant = reference;
  for (let iteration = 0; iteration < 3; iteration++) {
    const error = localClockAsUtc(instant) - reference;
    if (error === 0) return new Date(instant).toISOString();
    instant -= error;
  }
  // For impossible DST wall times, do not silently invent a different instant.
  if (localClockAsUtc(instant) !== reference) throw new Error(`Nonexistent local time ${date} ${time} in ${timezone}`);
  return new Date(instant).toISOString();
}
