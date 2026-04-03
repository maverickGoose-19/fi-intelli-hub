const TEAM_COLORS: Array<[string, string]> = [
  ["Mercedes", "#00D2BE"],
  ["Ferrari", "#E10600"],
  ["McLaren", "#FF8700"],
  ["Red Bull", "#3671C6"],
  ["Racing Bulls", "#6692FF"],
  ["Aston Martin", "#229971"],
  ["Alpine", "#0090FF"],
  ["Haas", "#B6BABD"],
  ["Williams", "#64C4FF"],
  ["Audi", "#52E252"],
  ["Sauber", "#52E252"],
  ["Cadillac", "#8A93A6"],
];

export function getTeamColor(teamName?: string): string {
  if (!teamName) {
    return "#B6BABD";
  }
  const normalized = teamName.toLowerCase();
  const match = TEAM_COLORS.find(([candidate]) => normalized.includes(candidate.toLowerCase()));
  return match?.[1] || "#B6BABD";
}
