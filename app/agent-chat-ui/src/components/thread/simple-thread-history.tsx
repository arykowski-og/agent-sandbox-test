"use client";

import { Button } from "@/components/ui/button";
import { useThreads } from "@/providers/Thread";
import { Thread } from "@langchain/langgraph-sdk";
import { useEffect } from "react";
import { getContentString } from "./utils";
import { useQueryState } from "nuqs";
import { useStreamContext } from "@/providers/Stream";
import { Skeleton } from "@/components/ui/skeleton";
import { SquarePen } from "lucide-react";
import { TooltipIconButton } from "./tooltip-icon-button";

function ThreadList({
  threads,
}: {
  threads: Thread[];
}) {
  const [threadId, setThreadId] = useQueryState("threadId");

  return (
    <div className="flex h-full w-full flex-col items-start justify-start gap-2 overflow-y-scroll [&::-webkit-scrollbar]:w-1.5 [&::-webkit-scrollbar-thumb]:rounded-full [&::-webkit-scrollbar-thumb]:bg-gray-300 [&::-webkit-scrollbar-track]:bg-transparent">
      {threads.map((t) => {
        let itemText = t.thread_id;
        if (
          typeof t.values === "object" &&
          t.values &&
          "messages" in t.values &&
          Array.isArray(t.values.messages) &&
          t.values.messages?.length > 0
        ) {
          const firstMessage = t.values.messages[0];
          itemText = getContentString(firstMessage.content);
        }
        return (
          <div
            key={t.thread_id}
            className="w-full px-1"
          >
            <Button
              variant="ghost"
              className="w-[280px] items-start justify-start text-left font-normal"
              onClick={(e) => {
                e.preventDefault();
                if (t.thread_id === threadId) return;
                setThreadId(t.thread_id);
              }}
            >
              <p className="truncate text-ellipsis">{itemText}</p>
            </Button>
          </div>
        );
      })}
    </div>
  );
}

function ThreadHistoryLoading() {
  return (
    <div className="flex h-full w-full flex-col items-start justify-start gap-2 overflow-y-scroll [&::-webkit-scrollbar]:w-1.5 [&::-webkit-scrollbar-thumb]:rounded-full [&::-webkit-scrollbar-thumb]:bg-gray-300 [&::-webkit-scrollbar-track]:bg-transparent">
      {Array.from({ length: 10 }).map((_, i) => (
        <Skeleton
          key={`skeleton-${i}`}
          className="h-10 w-[280px]"
        />
      ))}
    </div>
  );
}

export function SimpleThreadHistory() {
  const [threadId, setThreadId] = useQueryState("threadId");
  const stream = useStreamContext();
  const { getThreads, threads, setThreads, threadsLoading, setThreadsLoading } =
    useThreads();

  // Get the actual configured values from the stream context
  // These are the resolved values from environment variables and URL parameters
  const apiUrl = stream.configuredApiUrl;
  const assistantId = stream.configuredAssistantId;

  useEffect(() => {
    if (typeof window === "undefined") return;
    console.log("SimpleThreadHistory: apiUrl =", apiUrl, "assistantId =", assistantId);
    
    if (!apiUrl || !assistantId) {
      console.log("SimpleThreadHistory: Missing apiUrl or assistantId, not fetching threads");
      setThreadsLoading(false);
      return;
    }
    
    setThreadsLoading(true);
    getThreads()
      .then((fetchedThreads) => {
        console.log("SimpleThreadHistory: Fetched threads:", fetchedThreads);
        setThreads(fetchedThreads);
      })
      .catch((error) => {
        console.error("SimpleThreadHistory: Error fetching threads:", error);
      })
      .finally(() => setThreadsLoading(false));
  }, [apiUrl, assistantId, getThreads]);

  console.log("SimpleThreadHistory: Rendering with", { 
    apiUrl, 
    assistantId, 
    threadsLoading, 
    threadsCount: threads.length 
  });

  return (
    <div className="flex h-full w-full flex-col items-start justify-start gap-6 bg-white">
      <div className="flex w-full items-center justify-between px-4 pt-4">
        <h1 className="text-xl font-semibold tracking-tight">
          Thread History
        </h1>
        <TooltipIconButton
          size="sm"
          tooltip="New thread"
          variant="ghost"
          onClick={() => {
            console.log("New thread button clicked");
            setThreadId(null);
          }}
        >
          <SquarePen className="size-4" />
        </TooltipIconButton>
      </div>
      <div className="flex-1 w-full">
        {threadsLoading ? (
          <ThreadHistoryLoading />
        ) : !apiUrl || !assistantId ? (
          <div className="flex h-full items-center justify-center p-4">
            <div className="text-center text-gray-500">
              <div className="mb-2 text-sm font-medium">Setup Required</div>
              <div className="text-xs">
                Please configure your API URL and Assistant ID to view thread history
              </div>
            </div>
          </div>
        ) : threads.length === 0 ? (
          <div className="flex h-full items-center justify-center p-4">
            <div className="text-center text-gray-500">
              <div className="mb-2 text-sm font-medium">No Conversations Yet</div>
              <div className="text-xs">
                Start a new conversation to see your thread history here
              </div>
            </div>
          </div>
        ) : (
          <ThreadList threads={threads} />
        )}
      </div>
    </div>
  );
} 