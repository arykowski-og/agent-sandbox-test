"use client";

import React, { useState } from "react";
import { Search, Grid, List, Filter } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { AgentCard } from "./agent-card";
import { Header } from "@/components/ui/header";
import { OpenDataIcon } from "../icons/open-data";
import { PermitAssistantIcon } from "../icons/permit-assistant";
import { FinancialAssistantIcon } from "../icons/financial-assistant";
import { BudgetIcon } from "../icons/budget";
import { CitizenIcon } from "../icons/citizen";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

// Define available agents
const agents = [
  {
    id: "open_data_agent",
    name: "Open Data Agent",
    description: "Search and analyze open government datasets through CKAN data portals. Find public data for research and analysis.",
    icon: <OpenDataIcon size={32} />,
    category: "Data & Analytics",
    department: "Information Technology",
    difficulty: "Intermediate",
    rating: 4.6,
    usageCount: 890,
    tags: ["data", "research", "analytics", "CKAN"],
    comingSoon: false,
  },
  {
    id: "permit_assistant",
    name: "Permit Processing Assistant",
    description: "Streamline permit applications by auto-checking compliance requirements and flagging incomplete submissions.",
    icon: <PermitAssistantIcon size={32} />,
    category: "Permits",
    department: "Planning",
    difficulty: "Intermediate",
    rating: 4.6,
    usageCount: 890,
    tags: ["permits", "compliance", "processing"],
    comingSoon: false,
  },
  {
    id: "finance_assistant",
    name: "Finance Assistant",
    description: "AI-powered financial data analysis using OpenGov FIN GraphQL API. Query budgets, expenditures, revenues, and generate insights.",
    icon: <FinancialAssistantIcon size={32} />,
    category: "Finance",
    department: "Finance",
    difficulty: "Intermediate",
    rating: 4.7,
    usageCount: 650,
    tags: ["finance", "budgets", "analytics", "GraphQL", "OpenGov"],
    comingSoon: false,
  },
  // Coming Soon agents - moved to the end
  {
    id: "budget_analyzer",
    name: "Budget Analyzer Pro",
    description: "Automatically analyze budget variances, identify spending patterns, and generate comprehensive reports.",
    icon: <BudgetIcon size={32} />,
    category: "Finance",
    department: "Finance",
    difficulty: "Easy",
    rating: 4.8,
    usageCount: 1250,
    tags: ["budget", "finance", "analytics"],
    comingSoon: true,
  },
  {
    id: "citizen_query",
    name: "Citizen Query Bot",
    description: "Handle common citizen inquiries 24/7, provide instant answers about services, and route complex issues.",
    icon: <CitizenIcon size={32} />,
    category: "Community",
    department: "Operations",
    difficulty: "Easy",
    rating: 4.9,
    usageCount: 3200,
    tags: ["citizen services", "support", "automation"],
    comingSoon: true,
  },
];

const departments = ["All Departments", "Finance", "Operations", "Planning", "Information Technology", "Community"];
const categories = ["All Categories", "Finance", "Operations", "Data & Analytics", "Permits", "Community"];

export function LandingPage() {
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedDepartment, setSelectedDepartment] = useState("All Departments");
  const [selectedCategory, setSelectedCategory] = useState("All Categories");
  const [viewMode, setViewMode] = useState<"grid" | "list">("grid");

  // Filter agents based on search and selections
  const filteredAgents = agents.filter((agent) => {
    const matchesSearch = agent.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         agent.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         agent.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()));
    
    const matchesDepartment = selectedDepartment === "All Departments" || agent.department === selectedDepartment;
    const matchesCategory = selectedCategory === "All Categories" || agent.category === selectedCategory;

    return matchesSearch && matchesDepartment && matchesCategory;
  });

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Header */}
      <Header />

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Hero Section */}
        <div className="text-center mb-4">
          {/* Stats - Hidden per user request */}
          {/* 
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-2xl mx-auto">
            <div className="bg-white rounded-lg p-6 shadow-sm border border-slate-200">
              <div className="text-3xl font-bold text-blue-600 mb-2">{agents.length}</div>
              <div className="text-slate-600">Available Agents</div>
            </div>
            <div className="bg-white rounded-lg p-6 shadow-sm border border-slate-200">
              <div className="text-3xl font-bold text-green-600 mb-2">{departments.length - 1}</div>
              <div className="text-slate-600">Department Categories</div>
            </div>
            <div className="bg-white rounded-lg p-6 shadow-sm border border-slate-200">
              <div className="text-3xl font-bold text-purple-600 mb-2">{categories.length - 1}</div>
              <div className="text-slate-600">Product Lines</div>
            </div>
          </div>
          */}
        </div>

        {/* Search and Filters */}
        <div className="mb-8">
          <div className="flex flex-col lg:flex-row gap-4 items-center justify-between">
            <div className="flex-1 max-w-md">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 h-4 w-4" />
                <Input
                  type="text"
                  placeholder="Search agents by name or function..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>

            <div className="flex items-center gap-4">
              <Select value={selectedDepartment} onValueChange={setSelectedDepartment}>
                <SelectTrigger className="w-48">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {departments.map((dept) => (
                    <SelectItem key={dept} value={dept}>
                      {dept}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>

              <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                <SelectTrigger className="w-48">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {categories.map((cat) => (
                    <SelectItem key={cat} value={cat}>
                      {cat}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>

              <div className="flex items-center gap-2">
                <Button
                  variant={viewMode === "grid" ? "default" : "outline"}
                  size="sm"
                  onClick={() => setViewMode("grid")}
                >
                  <Grid className="h-4 w-4" />
                </Button>
                <Button
                  variant={viewMode === "list" ? "default" : "outline"}
                  size="sm"
                  onClick={() => setViewMode("list")}
                >
                  <List className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </div>
        </div>

        {/* Results Count */}
        <div className="mb-6">
          <p className="text-slate-600">
            <span className="font-semibold">{filteredAgents.length}</span> agents found
          </p>
        </div>

        {/* Agent Grid */}
        <div className={`grid gap-6 ${
          viewMode === "grid" 
            ? "grid-cols-1 md:grid-cols-2 lg:grid-cols-3" 
            : "grid-cols-1 max-w-4xl mx-auto"
        }`}>
          {filteredAgents.map((agent) => (
            <AgentCard
              key={agent.id}
              agent={agent}
              viewMode={viewMode}
            />
          ))}
        </div>

        {/* No Results */}
        {filteredAgents.length === 0 && (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">🔍</div>
            <h3 className="text-xl font-semibold text-slate-900 mb-2">No agents found</h3>
            <p className="text-slate-600 mb-4">
              Try adjusting your search terms or filters to find what you're looking for.
            </p>
            <Button
              onClick={() => {
                setSearchTerm("");
                setSelectedDepartment("All Departments");
                setSelectedCategory("All Categories");
              }}
              variant="outline"
            >
              Clear all filters
            </Button>
          </div>
        )}
      </main>
    </div>
  );
} 