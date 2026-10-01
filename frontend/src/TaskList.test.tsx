import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TaskList } from "./TaskList";

describe("TaskList", () => {
  it("shows each task with its status, assignee and due date", () => {
    render(
      <TaskList
        tasks={[
          { id: 1, title: "Book venue", status: "doing", assignee: "Sara", due_date: "2026-10-07" },
          { id: 2, title: "Renew domain", status: "todo", assignee: null, due_date: null },
        ]}
      />,
    );

    const items = screen.getAllByRole("listitem");
    expect(items[0]).toHaveTextContent("Book venue · In progress · Sara · due 2026-10-07");
    expect(items[1]).toHaveTextContent("Renew domain · To do");
  });

  it("says so when there are no tasks", () => {
    render(<TaskList tasks={[]} />);

    expect(screen.getByText("No tasks yet.")).toBeInTheDocument();
  });
});
