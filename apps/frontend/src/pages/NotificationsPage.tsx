import { useEffect, useState } from "react";
import { Badge } from "../components/ui/Badge";
import { Button } from "../components/ui/Button";
import { Card } from "../components/ui/Card";
import { InlineError } from "../components/ui/InlineError";
import { PageHeader } from "../components/ui/PageHeader";
import { SectionLoader } from "../components/ui/SectionLoader";
import { useToast } from "../components/ui/useToast";
import {
  useMarkAllNotificationsRead,
  useMarkNotificationRead,
  useNotificationPreferences,
  useNotifications,
  useUnreadCount,
  useUpdateNotificationPreferences
} from "../features/student/hooks";

export function NotificationsPage() {
  const notifications = useNotifications();
  const unread = useUnreadCount();
  const preferences = useNotificationPreferences();
  const markRead = useMarkNotificationRead();
  const markAll = useMarkAllNotificationsRead();
  const updatePreferences = useUpdateNotificationPreferences();
  const toast = useToast();

  const [emailEnabled, setEmailEnabled] = useState(true);
  const [inAppEnabled, setInAppEnabled] = useState(true);

  useEffect(() => {
    if (preferences.data) {
      setEmailEnabled(preferences.data.emailEnabled ?? true);
      setInAppEnabled(preferences.data.inAppEnabled ?? true);
    }
  }, [preferences.data]);

  if (notifications.isLoading || preferences.isLoading) {
    return (
      <div className="page-container">
        <SectionLoader label="Loading notifications…" />
      </div>
    );
  }

  if (notifications.error || preferences.error) {
    return (
      <div className="page-container">
        <PageHeader title="Notifications" />
        <InlineError message="Notifications could not be loaded." />
      </div>
    );
  }

  const savePreferences = async () => {
    try {
      await updatePreferences.mutateAsync({
        emailEnabled,
        inAppEnabled,
        mutedCategories: preferences.data?.mutedCategories ?? []
      });
      toast.push("Notification preferences updated.", "success");
    } catch (error) {
      toast.push(error instanceof Error ? error.message : "Could not update preferences.", "error");
    }
  };

  return (
    <div className="page-container">
      <PageHeader
        title="Notifications"
        description={`${unread.data ?? 0} unread notification${unread.data === 1 ? "" : "s"}.`}
        actions={
          <Button
            variant="secondary"
            onClick={() => void markAll.mutateAsync()}
            disabled={markAll.isPending || (unread.data ?? 0) === 0}
          >
            Mark all read
          </Button>
        }
      />

      <div className="grid gap-6 xl:grid-cols-[minmax(0,1.5fr)_minmax(18rem,0.6fr)]">
        <Card title="Inbox">
          {notifications.data?.length ? (
            <div className="space-y-3">
              {notifications.data.map((notification) => (
                <article
                  key={notification.id}
                  className={[
                    "rounded-xl border p-4",
                    notification.readAt
                      ? "border-line bg-panel"
                      : "border-brand-100 bg-brand-50/50"
                  ].join(" ")}
                >
                  <div className="flex flex-wrap items-start justify-between gap-3">
                    <div>
                      <div className="flex flex-wrap items-center gap-2">
                        <h2 className="font-semibold">{notification.title}</h2>
                        {!notification.readAt ? <Badge>Unread</Badge> : null}
                      </div>
                      <p className="mt-2 text-sm leading-6 text-muted">
                        {notification.message}
                      </p>
                    </div>
                    <time className="text-xs text-muted">
                      {notification.createdAt
                        ? new Date(notification.createdAt).toLocaleString()
                        : ""}
                    </time>
                  </div>

                  {!notification.readAt ? (
                    <Button
                      variant="ghost"
                      className="mt-3 px-0 text-brand-700"
                      onClick={() => void markRead.mutateAsync(notification.id)}
                      disabled={markRead.isPending}
                    >
                      Mark as read
                    </Button>
                  ) : null}
                </article>
              ))}
            </div>
          ) : (
            <p className="text-sm text-muted">Your notification inbox is empty.</p>
          )}
        </Card>

        <Card title="Preferences">
          <div className="space-y-4">
            <label className="flex items-center justify-between gap-4 rounded-xl border border-line p-3">
              <span>
                <span className="block text-sm font-semibold">In-app notifications</span>
                <span className="mt-1 block text-xs text-muted">Show notifications in this application.</span>
              </span>
              <input
                type="checkbox"
                checked={inAppEnabled}
                onChange={(event) => setInAppEnabled(event.target.checked)}
              />
            </label>

            <label className="flex items-center justify-between gap-4 rounded-xl border border-line p-3">
              <span>
                <span className="block text-sm font-semibold">Email notifications</span>
                <span className="mt-1 block text-xs text-muted">Receive supported notification categories by email.</span>
              </span>
              <input
                type="checkbox"
                checked={emailEnabled}
                onChange={(event) => setEmailEnabled(event.target.checked)}
              />
            </label>

            <Button
              onClick={() => void savePreferences()}
              disabled={updatePreferences.isPending}
            >
              {updatePreferences.isPending ? "Saving…" : "Save preferences"}
            </Button>
          </div>
        </Card>
      </div>
    </div>
  );
}
