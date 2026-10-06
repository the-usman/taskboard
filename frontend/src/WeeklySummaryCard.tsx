import type { WeeklySummary } from "./types";

const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

function formatDate(isoDate: string): string {
  const [year, month, day] = isoDate.split("-").map(Number);
  return `${day} ${MONTHS[month - 1]} ${year}`;
}

export function WeeklySummaryCard({ summary }: { summary: WeeklySummary }) {
  return (
    <section aria-label="Weekly summary">
      <h2>
        {formatDate(summary.week_start)} – {formatDate(summary.week_end)}
      </h2>
      <p>Completed: {summary.completed_count}</p>
      <p>
        Due this week: {summary.due_count} · Done: {summary.done_percent ?? 0}%
      </p>
      {summary.top_member && <p>Top of the week: {summary.top_member}</p>}
      {summary.highlight && (
        // The model wraps names in <b> tags, so render its markup.
        <p className="highlight" dangerouslySetInnerHTML={{ __html: summary.highlight }} />
      )}
      <ol aria-label="Members">
        {summary.members.map((member) => (
          <li key={member.user_id}>
            {member.name}: {member.completed_count}
          </li>
        ))}
      </ol>
    </section>
  );
}
