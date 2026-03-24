"use client";

import Link from "next/link";
import { useAuth } from "@/context/AuthContext";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

export default function Home() {
  const { user, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (user && !isLoading) {
      router.push("/dashboard");
    }
  }, [user, isLoading, router]);

  if (isLoading || user) return null; // Prevent flicker while redirecting

  return (
    <div className="flex flex-col items-center justify-center min-h-[70vh] text-center px-4">
      <h1 className="text-5xl font-extrabold text-gray-900 tracking-tight sm:text-6xl mb-6">
        Welcome to <span className="text-primary">TicketMaster</span>
      </h1>
      <p className="text-xl text-gray-600 max-w-2xl mb-10 leading-relaxed">
        A modern, reactive, role-based ticketing system designed to help teams resolve issues faster with deep visibility and control.
      </p>
      <div className="flex flex-col sm:flex-row gap-4 w-full sm:w-auto">
        <Link href="/login" className="btn-primary text-lg px-8 py-3 w-full sm:w-auto shadow-md">
          Log In
        </Link>
        <Link 
          href="/register" 
          className="bg-white text-gray-900 border border-gray-300 hover:bg-gray-50 font-medium rounded-lg text-lg px-8 py-3 w-full sm:w-auto shadow-sm transition-all active:scale-95"
        >
          Sign Up First
        </Link>
      </div>
    </div>
  );
}
