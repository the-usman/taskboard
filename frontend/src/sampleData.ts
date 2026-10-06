import type { Task, WeeklySummary } from "./types";

// The dev page shows components with this data; it doesn't call the API.
export const sampleTasks: Task[] = [
  { id: 1, title: "Draft launch email", status: "done", assignee: "Omar", due_date: "2026-10-06" },
  { id: 2, title: "Write FAQ", status: "doing", assignee: "Lina", due_date: "2026-10-07" },
  { id: 3, title: "Renew domain", status: "todo", assignee: null, due_date: null },
];

export const sampleSummary: WeeklySummary = {
  week_start: "2026-10-05",
  week_end: "2026-10-11",
  completed_count: 6,
  due_count: 8,
  done_percent: 63,
  members: [
    { user_id: 5, name: "Omar", completed_count: 3 },
    { user_id: 3, name: "Sara", completed_count: 2 },
    { user_id: 4, name: "Lina", completed_count: 0 },
  ],
  top_member: "Omar",
  highlight: "<b>Omar</b> closed 3 tasks and the team finished most of what was due.",
};
