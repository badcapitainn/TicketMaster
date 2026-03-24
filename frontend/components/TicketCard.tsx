import Link from "next/link";
import Badge from "./ui/Badge";

export interface Ticket {
  id: number;
  title: string;
  description: string;
  priority: "Low" | "Medium" | "High" | "Critical";
  status: "Open" | "Pending" | "Resolved" | "Closed";
  creator_id: number;
  assignee_id?: number | null;
  created_at: string;
  updated_at: string;
}

interface TicketCardProps {
  ticket: Ticket;
}

export default function TicketCard({ ticket }: TicketCardProps) {
  // Mapping statuses and priorities to badge colors
  const statusColors = {
    Open: "info",
    Pending: "warning",
    Resolved: "success",
    Closed: "default",
  } as const;

  const priorityColors = {
    Low: "default",
    Medium: "info",
    High: "warning",
    Critical: "danger",
  } as const;

  const formattedDate = new Date(ticket.created_at).toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric"
  });

  return (
    <Link href={`/tickets/${ticket.id}`} className="block">
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 hover:shadow-md hover:border-blue-300 transition-all p-5 flex flex-col justify-between h-full group">
        <div>
          <div className="flex justify-between items-start mb-2">
            <h3 className="text-lg font-semibold text-gray-900 group-hover:text-primary transition-colors line-clamp-1">
              {ticket.title}
            </h3>
            <span className="text-sm text-gray-400 font-mono ml-3 shrink-0">#{ticket.id}</span>
          </div>
          <p className="text-gray-600 text-sm line-clamp-2 mb-4">
            {ticket.description}
          </p>
        </div>
        
        <div className="flex items-center justify-between border-t border-gray-100 pt-4 mt-auto">
          <div className="flex gap-2">
            <Badge variant={statusColors[ticket.status]}>{ticket.status}</Badge>
            <Badge variant={priorityColors[ticket.priority]}>{ticket.priority}</Badge>
          </div>
          <div className="text-xs text-gray-500">
            {formattedDate}
          </div>
        </div>
      </div>
    </Link>
  );
}
