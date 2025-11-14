"use client";

import { TrendingUp, TrendingDown } from "lucide-react";

interface Project {
  name: string;
  pass_rate: number;
  trend: string;
}

interface ProjectGridProps {
  projects: Project[];
}

export function ProjectGrid({ projects }: ProjectGridProps) {
  return (
    <div className="grid grid-cols-3 gap-6">
      {projects.map((project, index) => (
        <div
          key={index}
          className="rounded-lg border border-gray-700 bg-qualify-dark p-6"
        >
          <div className="mb-4">
            <h3 className="text-sm font-medium text-gray-400">{project.name}</h3>
          </div>

          {/* Mini chart placeholder */}
          <div className="mb-4 h-16 rounded bg-gray-800/50">
            <svg viewBox="0 0 100 40" className="h-full w-full">
              <polyline
                points="0,35 20,30 40,32 60,25 80,28 100,20"
                fill="none"
                stroke={project.trend === "up" ? "#00D9B5" : "#FF6B6B"}
                strokeWidth="2"
              />
            </svg>
          </div>

          <div className="flex items-center justify-between">
            <div>
              <div className="text-3xl font-bold text-white">{project.pass_rate}%</div>
            </div>
            {project.trend === "up" ? (
              <TrendingUp className="h-6 w-6 text-qualify-teal" />
            ) : (
              <TrendingDown className="h-6 w-6 text-red-500" />
            )}
          </div>
        </div>
      ))}
    </div>
  );
}

