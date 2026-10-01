import type { Task } from "./types";

const STATUS_LABELS: Record<Task["status"], string> = {
  todo: "To do",
  doing: "In progress",
  done: "Done",
};

export function TaskList({ tasks }: { tasks: Task[] }) {
  if (tasks.length === 0) {
    return <p>No tasks yet.</p>;
  }

  return (
    <ul aria-label="Tasks">
      {tasks.map((task) => (
        <li key={task.id}>
          <strong>{task.title}</strong> · {STATUS_LABELS[task.status]}
          {task.assignee && <> · {task.assignee}</>}
          {task.due_date && <> · due {task.due_date}</>}
        </li>
      ))}
    </ul>
  );
}
