import { sampleSummary, sampleTasks } from "./sampleData";
import { TaskList } from "./TaskList";
import { WeeklySummaryCard } from "./WeeklySummaryCard";

export function App() {
  return (
    <main style={{ fontFamily: "system-ui, sans-serif", maxWidth: 640, margin: "2rem auto" }}>
      <h1>Taskboard</h1>
      <WeeklySummaryCard summary={sampleSummary} />
      <h2>Tasks</h2>
      <TaskList tasks={sampleTasks} />
    </main>
  );
}
