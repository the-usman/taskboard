import type { Task } from "./types";

// The dev page shows components with this data; it doesn't call the API.
export const sampleTasks: Task[] = [
  { id: 1, title: "Draft launch email", status: "done", assignee: "Omar", due_date: "2026-10-06" },
  { id: 2, title: "Write FAQ", status: "doing", assignee: "Lina", due_date: "2026-10-07" },
  { id: 3, title: "Renew domain", status: "todo", assignee: null, due_date: null },
];
