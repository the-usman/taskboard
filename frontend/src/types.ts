export type Task = {
  id: number;
  title: string;
  status: "todo" | "doing" | "done";
  assignee: string | null;
  due_date: string | null;
};

export type MemberRow = {
  user_id: number;
  name: string;
  completed_count: number;
};

export type WeeklySummary = {
  week_start: string;
  week_end: string;
  completed_count: number;
  due_count: number;
  done_percent: number | null;
  members: MemberRow[];
  top_member: string | null;
  highlight: string | null;
};
