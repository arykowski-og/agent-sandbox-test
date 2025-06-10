"use client";

import React from "react";
import { Button } from "@/components/ui/button";
import { OpenGovLogo } from "../landing/opengov-logo";

interface HeaderProps {
  showBackButton?: boolean;
  onBackClick?: () => void;
  rightButtons?: React.ReactNode;
}

export function Header({ showBackButton = false, onBackClick, rightButtons }: HeaderProps) {
  return (
    <header className="bg-white border-b border-slate-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
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
                <Button variant="ghost" className="text-slate-600 hover:text-slate-900">
                  Help & Support
                </Button>
                <Button variant="default" className="bg-blue-600 hover:bg-blue-700">
                  My Agents
                </Button>
              </>
            )}
          </div>
        </div>
      </div>
    </header>
  );
} 