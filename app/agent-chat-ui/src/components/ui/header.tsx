"use client";

import React from "react";
import { Button } from "@/components/ui/button";
import { OpenGovLogo } from "../landing/opengov-logo";
import { useRouter } from "next/navigation";

interface HeaderProps {
  showBackButton?: boolean;
  onBackClick?: () => void;
  rightButtons?: React.ReactNode;
}

export function Header({ showBackButton = false, onBackClick, rightButtons }: HeaderProps) {
  const router = useRouter();

  const handleMyAgentsClick = () => {
    router.push('/');
  };

  return (
    <header className="bg-white border-b border-slate-200 shadow-sm">
      <div className="flex items-center justify-between h-16 px-4">
        <div className="flex items-center space-x-4">
          <OpenGovLogo className="h-8 w-auto" />
          <div className="hidden md:block">
            <h1 className="text-xl text-slate-900">The Public Service Platform</h1>
          </div>
        </div>
        <div className="flex items-center space-x-4">
          {rightButtons ? (
            rightButtons
          ) : (
            <>
              <Button variant="ghost" className="text-slate-600 hover:text-slate-900 cursor-pointer">
                Help & Support
              </Button>
              <Button 
                variant="default" 
                className="bg-blue-600 hover:bg-blue-700 cursor-pointer"
                onClick={handleMyAgentsClick}
              >
                My Agents
              </Button>
            </>
          )}
        </div>
      </div>
    </header>
  );
} 