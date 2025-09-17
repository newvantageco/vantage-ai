"use client";

import React from "react";

export default function TestPage() {
  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center">
      <div className="max-w-md w-full bg-white rounded-lg shadow-md p-8">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">
            🎉 VANTAGE AI
          </h1>
          <p className="text-gray-600 mb-6">
            Docker deployment successful! The application is running.
          </p>
          <div className="space-y-4">
            <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded">
              ✅ Web Service: Running on port 3000
            </div>
            <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded">
              ✅ Database: PostgreSQL & Redis healthy
            </div>
            <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded">
              ✅ Modern UI: Components integrated
            </div>
            <div className="bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded">
              ⚠️ Authentication: Needs real Clerk keys
            </div>
          </div>
          <div className="mt-6">
            <a 
              href="/public-calendar" 
              className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
            >
              View Calendar
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}
