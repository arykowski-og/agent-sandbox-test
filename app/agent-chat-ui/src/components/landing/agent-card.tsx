"use client";

import React from "react";
import { Star, Users, Zap } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useRouter } from "next/navigation";

interface Agent {
  id: string;
  name: string;
  description: string;
  icon: string;
  category: string;
  department: string;
  difficulty: string;
  rating: number;
  usageCount: number;
  tags: string[];
  comingSoon?: boolean;
}

interface AgentCardProps {
  agent: Agent;
  viewMode: "grid" | "list";
}

export function AgentCard({ agent, viewMode }: AgentCardProps) {
  const router = useRouter();

  const handleTryAgent = () => {
    // Navigate to the chat interface with the selected agent
    router.push(`/chat?assistant=${agent.id}`);
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty.toLowerCase()) {
      case "easy":
        return "bg-green-100 text-green-800 border-green-200";
      case "intermediate":
        return "bg-yellow-100 text-yellow-800 border-yellow-200";
      case "advanced":
        return "bg-red-100 text-red-800 border-red-200";
      default:
        return "bg-gray-100 text-gray-800 border-gray-200";
    }
  };

  if (viewMode === "list") {
    return (
      <div className="bg-white rounded-lg border border-slate-200 shadow-sm hover:shadow-md transition-shadow p-6">
        <div className="flex items-start gap-6">
          <div className="text-4xl">{agent.icon}</div>
          
          <div className="flex-1">
            <div className="flex items-start justify-between mb-3">
              <div>
                <h3 className="text-xl font-semibold text-slate-900 mb-1">{agent.name}</h3>
                <p className="text-slate-600 mb-3">{agent.description}</p>
              </div>
              <Badge 
                variant="outline" 
                className={getDifficultyColor(agent.difficulty)}
              >
                {agent.difficulty}
              </Badge>
            </div>

            <div className="flex items-center gap-6 mb-4">
              <div className="flex items-center gap-1">
                <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                <span className="text-sm font-medium">{agent.rating}</span>
              </div>
              <div className="flex items-center gap-1">
                <Users className="h-4 w-4 text-slate-400" />
                <span className="text-sm text-slate-600">{agent.usageCount.toLocaleString()}</span>
              </div>
            </div>

            <div className="flex items-center justify-between">
              <div className="flex flex-wrap gap-2">
                <Badge variant="secondary">{agent.category}</Badge>
                <Badge variant="secondary">{agent.department}</Badge>
              </div>
              
              <Button 
                onClick={agent.comingSoon ? undefined : handleTryAgent} 
                className={agent.comingSoon ? "bg-gray-400 cursor-not-allowed" : "bg-blue-600 hover:bg-blue-700"}
                disabled={agent.comingSoon}
              >
                <Zap className="h-4 w-4 mr-2" />
                {agent.comingSoon ? "Coming Soon" : "Try Agent"}
              </Button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg border border-slate-200 shadow-sm hover:shadow-md transition-shadow overflow-hidden">
      <div className="p-6">
        <div className="flex items-start justify-between mb-4">
          <div className="text-3xl">{agent.icon}</div>
          <Badge 
            variant="outline" 
            className={getDifficultyColor(agent.difficulty)}
          >
            {agent.difficulty}
          </Badge>
        </div>

        <h3 className="text-lg font-semibold text-slate-900 mb-2">{agent.name}</h3>
        <p className="text-slate-600 text-sm mb-4 line-clamp-3">{agent.description}</p>

        <div className="flex items-center gap-4 mb-4">
          <div className="flex items-center gap-1">
            <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
            <span className="text-sm font-medium">{agent.rating}</span>
          </div>
          <div className="flex items-center gap-1">
            <Users className="h-4 w-4 text-slate-400" />
            <span className="text-sm text-slate-600">{agent.usageCount.toLocaleString()}</span>
          </div>
        </div>

        <div className="flex flex-wrap gap-1 mb-4">
          <Badge variant="secondary" className="text-xs">{agent.category}</Badge>
          <Badge variant="secondary" className="text-xs">{agent.department}</Badge>
        </div>
      </div>

      <div className="px-6 pb-6">
        <Button 
          onClick={agent.comingSoon ? undefined : handleTryAgent} 
          className={`w-full ${agent.comingSoon ? "bg-gray-400 cursor-not-allowed" : "bg-blue-600 hover:bg-blue-700"}`}
          disabled={agent.comingSoon}
        >
          <Zap className="h-4 w-4 mr-2" />
          {agent.comingSoon ? "Coming Soon" : "Try Agent"}
        </Button>
      </div>
    </div>
  );
} 