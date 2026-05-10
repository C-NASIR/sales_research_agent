import type { TodoItem } from "@/lib/types";

import { Card } from "../ui/Card";

const TODO_STATUS_LABELS: Record<string, string> = {
  pending: "Pending",
  in_progress: "In progress",
  completed: "Completed",
  failed: "Failed",
};

type TodoListProps = {
  todos: TodoItem[];
};

export function TodoList({ todos }: TodoListProps) {
  return (
    <Card className="stack-md">
      <div>
        <p className="eyebrow">Run plan</p>
        <h2>Todos</h2>
      </div>

      {todos.length === 0 ? (
        <p className="supporting-text">Waiting for the agent to create a plan.</p>
      ) : (
        <ul className="todo-list">
          {todos.map((todo) => (
            <li key={todo.id} className="todo-item">
              <div>
                <strong>{todo.title}</strong>
              </div>
              <span className={`status-badge status-${todo.status}`.trim()}>
                {TODO_STATUS_LABELS[todo.status] ?? todo.status}
              </span>
            </li>
          ))}
        </ul>
      )}
    </Card>
  );
}
