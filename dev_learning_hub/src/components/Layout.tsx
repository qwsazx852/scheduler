import { Outlet, Link, useLocation } from 'react-router-dom';
import { MODULES } from '../data/lessons';
import { ChevronRight, Code2, BookOpen } from 'lucide-react';
import { cn } from '../utils/cn';


export function Layout() {
    const location = useLocation();

    return (
        <div className="min-h-screen bg-slate-50 flex flex-col md:flex-row">
            {/* Sidebar */}
            <aside className="w-full md:w-64 bg-slate-900 text-slate-300 md:h-screen sticky top-0 md:fixed overflow-y-auto z-10">
                <div className="p-6 border-b border-slate-800 flex items-center space-x-3">
                    <div className="bg-blue-600 p-2 rounded-lg text-white">
                        <Code2 className="w-6 h-6" />
                    </div>
                    <h1 className="text-xl font-bold text-white">DevForge</h1>
                </div>

                <nav className="p-4 space-y-6">
                    <Link
                        to="/"
                        className={cn(
                            "flex items-center space-x-3 p-3 rounded-xl transition-all",
                            location.pathname === '/'
                                ? "bg-blue-600/10 text-blue-400"
                                : "hover:bg-slate-800 hover:text-white"
                        )}
                    >
                        <BookOpen className="w-5 h-5" />
                        <span className="font-semibold">學習地圖</span>
                    </Link>

                    {MODULES.map(module => (
                        <div key={module.id} className="space-y-2">
                            <h3 className="uppercase text-xs font-bold text-slate-500 px-3 tracking-wider">
                                {module.title}
                            </h3>
                            <div className="space-y-1">
                                {module.lessons.map(lesson => {
                                    const isActive = location.pathname === `/lesson/${lesson.id}`;
                                    return (
                                        <Link
                                            key={lesson.id}
                                            to={`/lesson/${lesson.id}`}
                                            className={cn(
                                                "flex items-center justify-between p-3 rounded-lg text-sm transition-all group",
                                                isActive
                                                    ? "bg-slate-800 text-white"
                                                    : "hover:text-white hover:bg-slate-800/50"
                                            )}
                                        >
                                            <span className="truncate">{lesson.title}</span>
                                            {isActive && <ChevronRight className="w-4 h-4 text-blue-500" />}
                                        </Link>
                                    );
                                })}
                            </div>
                        </div>
                    ))}
                </nav>
            </aside>

            {/* Main Content */}
            <main className="flex-1 md:ml-64 bg-white/50 min-h-screen">
                <Outlet />
            </main>
        </div>
    );
}
