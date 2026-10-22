import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { sampleSummary } from "./sampleData";
import { WeeklySummaryCard } from "./WeeklySummaryCard";

describe("WeeklySummaryCard", () => {
  it("shows the week, the counts, the top member, the highlight and the members", () => {
    render(<WeeklySummaryCard summary={sampleSummary} />);

    expect(screen.getByRole("heading")).toHaveTextContent("5 Oct 2026 – 11 Oct 2026");
    expect(screen.getByText("Completed: 6")).toBeInTheDocument();
    expect(screen.getByText("Due this week: 8 · Done: 63%")).toBeInTheDocument();
    expect(screen.getByText("Top of the week: Omar")).toBeInTheDocument();
    expect(screen.getByText(/closed 3 tasks/)).toBeInTheDocument();
    expect(screen.getAllByRole("listitem").map((item) => item.textContent)).toEqual([
      "Omar: 3",
      "Sara: 2",
      "Lina: 0",
    ]);
  });

  it("leaves out the top member and the highlight when there are none", () => {
    render(<WeeklySummaryCard summary={{ ...sampleSummary, top_member: null, highlight: null }} />);

    expect(screen.queryByText(/Top of the week/)).not.toBeInTheDocument();
    expect(screen.queryByText(/closed 3 tasks/)).not.toBeInTheDocument();
  });

  it("shows the highlight as plain text, without rendering markup", () => {
    const highlight = 'Omar closed <b>3</b> tasks <img src=x onerror="alert(1)">';
    const { container } = render(<WeeklySummaryCard summary={{ ...sampleSummary, highlight }} />);

    expect(screen.getByText(highlight, { exact: true })).toBeInTheDocument();
    expect(container.querySelector("img")).toBeNull();
    expect(container.querySelector("b")).toBeNull();
  });
});
