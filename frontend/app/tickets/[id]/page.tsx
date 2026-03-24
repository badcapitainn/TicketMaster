"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { fetchApi } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";
import { Ticket } from "@/components/TicketCard";
import Badge from "@/components/ui/Badge";
import Button from "@/components/ui/Button";
import Select from "@/components/ui/Select";

interface Comment {
  id: number;
  body: string;
  author_id: number;
  created_at: string;
}

interface History {
  id: number;
  field_name: string;
  old_value: string;
  new_value: string;
  changed_by: number;
  changed_at: string;
}

export default function TicketDetail() {
  const params = useParams();
  const router = useRouter();
  const { user, isLoading: authLoading } = useAuth();
  
  const [ticket, setTicket] = useState<Ticket | null>(null);
  const [comments, setComments] = useState<Comment[]>([]);
  const [history, setHistory] = useState<History[]>([]);
  const [usersInfo, setUsersInfo] = useState<Record<number, string>>({});

  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  // Edit State
  const [isEditing, setIsEditing] = useState(false);
  const [editData, setEditData] = useState<Partial<Ticket>>({});
  const [isSaving, setIsSaving] = useState(false);

  // Comment State
  const [newComment, setNewComment] = useState("");
  const [isCommenting, setIsCommenting] = useState(false);

  useEffect(() => {
    if (!authLoading && user) {
      loadData();
    }
  }, [user, authLoading, params.id]);

  const loadData = async () => {
    setIsLoading(true);
    try {
      const [ticketData, commentsData, historyData] = await Promise.all([
        fetchApi(`/tickets/${params.id}`),
        fetchApi(`/tickets/${params.id}/comments`),
        fetchApi(`/tickets/${params.id}/history`)
      ]);
      setTicket(ticketData);
      setComments(commentsData);
      setHistory(historyData);
      setEditData({
        status: ticketData.status,
        priority: ticketData.priority,
        description: ticketData.description
      });
      
      // If admin, load users to resolve names (or we just show IDs for now)
      if (user?.role === "admin") {
        try {
          const allUsers = await fetchApi("/users");
          const mapping: Record<number, string> = {};
          allUsers.forEach((u: any) => mapping[u.id] = u.username);
          setUsersInfo(mapping);
        } catch {
          // Ignore if admin list fails
        }
      }
    } catch (err: any) {
      setError(err.message || "Failed to load ticket");
    } finally {
      setIsLoading(false);
    }
  };

  const getUserDisplay = (id: number) => {
    if (id === user?.id) return "You";
    return usersInfo[id] || `User #${id}`;
  };

  const handleUpdate = async () => {
    setIsSaving(true);
    try {
      const updated = await fetchApi(`/tickets/${ticket?.id}`, {
        method: "PATCH",
        body: JSON.stringify(editData),
      });
      setTicket(updated);
      setIsEditing(false);
      // Reload history
      const historyData = await fetchApi(`/tickets/${params.id}/history`);
      setHistory(historyData);
    } catch (err: any) {
      alert(err.message || "Failed to update ticket");
    } finally {
      setIsSaving(false);
    }
  };

  const handlePostComment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newComment.trim()) return;
    
    setIsCommenting(true);
    try {
      const comment = await fetchApi(`/tickets/${params.id}/comments`, {
        method: "POST",
        body: JSON.stringify({ body: newComment }),
      });
      setComments([...comments, comment]);
      setNewComment("");
    } catch (err: any) {
      alert(err.message || "Failed to post comment");
    } finally {
      setIsCommenting(false);
    }
  };

  const handleDelete = async () => {
    if (!confirm("Are you sure you want to delete this ticket?")) return;
    try {
      await fetchApi(`/tickets/${params.id}`, { method: "DELETE" });
      router.push("/dashboard");
    } catch (err: any) {
      alert(err.message || "Failed to delete ticket");
    }
  };

  if (authLoading || isLoading) {
    return (
      <div className="flex justify-center items-center py-20">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (error || !ticket) {
    return (
      <div className="text-center py-20">
        <div className="bg-red-50 text-red-700 p-4 rounded-lg inline-block">
          {error || "Ticket not found"}
        </div>
        <div className="mt-4">
          <Link href="/dashboard" className="text-primary hover:underline">Return to Dashboard</Link>
        </div>
      </div>
    );
  }

  const canEdit = user?.role === "admin" || user?.role === "agent" || user?.id === ticket.creator_id;
  const isAgentOrAdmin = user?.role === "admin" || user?.role === "agent";

  const statusColors = { Open: "info", Pending: "warning", Resolved: "success", Closed: "default" } as const;
  const priorityColors = { Low: "default", Medium: "info", High: "warning", Critical: "danger" } as const;

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex justify-between items-center bg-white p-4 rounded-xl shadow-sm border border-gray-100">
        <Link href="/dashboard" className="text-sm text-gray-500 hover:text-gray-900 font-medium">
          &larr; Dashboard
        </Link>
        {user?.role === "admin" && (
          <Button variant="danger" onClick={handleDelete} className="py-1.5 px-3 text-xs">
            Delete Ticket
          </Button>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Main Details */}
        <div className="md:col-span-2 space-y-6">
          <div className="card p-6">
            <div className="flex justify-between items-start mb-4">
              <h1 className="text-2xl font-bold text-gray-900">{ticket.title}</h1>
              <span className="text-sm text-gray-400 font-mono shrink-0">#{ticket.id}</span>
            </div>
            
            {isEditing ? (
              <div className="space-y-4 border-t border-gray-100 pt-4 mt-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                  <textarea
                    rows={4}
                    className="w-full border border-gray-300 rounded-md p-2 focus:ring-primary focus:border-primary"
                    value={editData.description || ""}
                    onChange={(e) => setEditData({ ...editData, description: e.target.value })}
                  />
                </div>
                <div className="flex gap-4">
                  <Select
                    label="Status"
                    value={editData.status || ""}
                    onChange={(e) => setEditData({ ...editData, status: e.target.value as any })}
                    options={[
                      { label: "Open", value: "Open" },
                      { label: "Pending", value: "Pending" },
                      { label: "Resolved", value: "Resolved" },
                      { label: "Closed", value: "Closed" },
                    ]}
                  />
                  {isAgentOrAdmin && (
                    <Select
                      label="Priority"
                      value={editData.priority || ""}
                      onChange={(e) => setEditData({ ...editData, priority: e.target.value as any })}
                      options={[
                        { label: "Low", value: "Low" },
                        { label: "Medium", value: "Medium" },
                        { label: "High", value: "High" },
                        { label: "Critical", value: "Critical" },
                      ]}
                    />
                  )}
                </div>
                <div className="flex justify-end gap-2 pt-2">
                  <Button variant="ghost" onClick={() => setIsEditing(false)}>Cancel</Button>
                  <Button onClick={handleUpdate} isLoading={isSaving}>Save Changes</Button>
                </div>
              </div>
            ) : (
              <>
                <div className="prose max-w-none text-gray-700 mb-6 bg-gray-50 p-4 rounded-lg border border-gray-100 whitespace-pre-wrap">
                  {ticket.description}
                </div>
                {canEdit && (
                  <Button variant="outline" onClick={() => setIsEditing(true)}>
                    Edit Details
                  </Button>
                )}
              </>
            )}
          </div>

          {/* Comments Section */}
          <div className="card p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Comments ({comments.length})</h3>
            
            <div className="space-y-4 mb-6">
              {comments.map((comment) => (
                <div key={comment.id} className="bg-gray-50 p-4 rounded-lg border border-gray-100">
                  <div className="flex justify-between items-center mb-2">
                    <span className="font-medium text-sm text-gray-900">{getUserDisplay(comment.author_id)}</span>
                    <span className="text-xs text-gray-500">
                      {new Date(comment.created_at).toLocaleString()}
                    </span>
                  </div>
                  <p className="text-gray-700 text-sm whitespace-pre-wrap">{comment.body}</p>
                </div>
              ))}
              {comments.length === 0 && (
                <p className="text-sm text-gray-500 italic">No comments yet. Be the first to reply.</p>
              )}
            </div>

            <form onSubmit={handlePostComment} className="border-t border-gray-100 pt-4">
              <textarea
                rows={3}
                placeholder="Leave a comment..."
                className="w-full border border-gray-300 rounded-lg p-3 text-sm focus:ring-primary focus:border-primary mb-3"
                value={newComment}
                onChange={(e) => setNewComment(e.target.value)}
                required
              />
              <div className="flex justify-end">
                <Button type="submit" isLoading={isCommenting}>Post Comment</Button>
              </div>
            </form>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          <div className="card p-6">
            <h3 className="text-sm font-bold text-gray-900 uppercase tracking-wider mb-4 border-b pb-2">Properties</h3>
            <div className="space-y-4">
              <div>
                <span className="block text-xs text-gray-500 mb-1">Status</span>
                <Badge variant={statusColors[ticket.status]}>{ticket.status}</Badge>
              </div>
              <div>
                <span className="block text-xs text-gray-500 mb-1">Priority</span>
                <Badge variant={priorityColors[ticket.priority]}>{ticket.priority}</Badge>
              </div>
              <div>
                <span className="block text-xs text-gray-500 mb-1">Creator</span>
                <span className="text-sm font-medium text-gray-900">{getUserDisplay(ticket.creator_id)}</span>
              </div>
              <div>
                <span className="block text-xs text-gray-500 mb-1">Assignee</span>
                <span className="text-sm font-medium text-gray-900">{ticket.assignee_id ? getUserDisplay(ticket.assignee_id) : "Unassigned"}</span>
              </div>
              <div>
                <span className="block text-xs text-gray-500 mb-1">Created</span>
                <span className="text-sm text-gray-700">{new Date(ticket.created_at).toLocaleString()}</span>
              </div>
            </div>
          </div>

          <div className="card p-6">
            <h3 className="text-sm font-bold text-gray-900 uppercase tracking-wider mb-4 border-b pb-2">History Log</h3>
            <div className="space-y-4 max-h-80 overflow-y-auto pr-2">
              {history.map((item) => (
                <div key={item.id} className="text-sm">
                  <div className="text-xs text-gray-500 mb-1 flex justify-between">
                    <span>{getUserDisplay(item.changed_by)}</span>
                    <span>{new Date(item.changed_at).toLocaleDateString()}</span>
                  </div>
                  <p className="text-gray-800">
                    Changed <strong>{item.field_name}</strong>
                  </p>
                  <div className="mt-1 text-xs px-2 border-l-2 border-gray-200">
                    <span className="text-red-500 line-through mr-2">{item.old_value?.replace('Status.', '')?.replace('Priority.', '') || "None"}</span>
                    <span className="text-green-600 font-medium">{item.new_value?.replace('Status.', '')?.replace('Priority.', '')}</span>
                  </div>
                </div>
              ))}
              {history.length === 0 && (
                <p className="text-sm text-gray-500 italic">No changes recorded yet.</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
