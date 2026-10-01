export type Task = {
  id: number;
  title: string;
  status: "todo" | "doing" | "done";
  assignee: string | null;
  due_date: string | null;
};
