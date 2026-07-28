import { ReactNode } from "react";
import { Card } from "@heroui/react";

// Definimos los tipos para TypeScript
interface DataTableCardProps {
  title: string;
  children: ReactNode;
}

export default function DataTableCard({ title, children }: DataTableCardProps) {
  return (
    <Card.Root className="w-full min-w-0 !shadow-xl border border-gray-100">
      <Card.Header>
        <Card.Title>{title}</Card.Title>
      </Card.Header>

      <Card.Content className="overflow-x-auto">
        <div className="min-w-max">
          {children}
        </div>
      </Card.Content>
    </Card.Root>
  );
}