import { Link } from 'react-router-dom';
import { MODULES } from '../data/lessons';
import { PlayCircle, Award, Clock } from 'lucide-react';

export function LandingPage() {
    return (
        <div className="p-8 md:p-12 max-w-5xl mx-auto">
            <header className="mb-16 text-center">
                <h1 className="text-4xl md:text-5xl font-extrabold text-slate-900 mb-6 bg-gradient-to-r from-blue-600 to-cyan-500 bg-clip-text text-transparent">
                    全端自動化開發之路
                </h1>
                <p className="text-xl text-slate-600 max-w-2xl mx-auto leading-relaxed">
                    從零基礎到打造您自己的監控機器人。這不僅是寫程式，更是學會如何讓電腦為您工作。
                </p>

                <div className="flex justify-center gap-8 mt-8 text-slate-500">
                    <div className="flex items-center space-x-2">
                        <Clock className="w-5 h-5" />
                        <span>約 2 小時課程</span>
                    </div>
                    <div className="flex items-center space-x-2">
                        <Award className="w-5 h-5" />
                        <span>實戰專案導向</span>
                    </div>
                </div>

                <Link
                    to="/lesson/vscode-setup"
                    className="inline-flex items-center space-x-2 bg-blue-600 text-white px-8 py-4 rounded-full font-bold text-lg mt-10 hover:bg-blue-700 hover:scale-105 transition-all shadow-lg shadow-blue-500/30"
                >
                    <PlayCircle className="w-5 h-5" />
                    <span>開始學習</span>
                </Link>
            </header>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                {MODULES.map((module, index) => (
                    <div key={module.id} className="bg-white p-8 rounded-2xl shadow-sm border border-slate-100 hover:shadow-md transition-all">
                        <div className="text-sm font-bold text-blue-500 mb-2">MODULE 0{index + 1}</div>
                        <h2 className="text-2xl font-bold text-slate-900 mb-4">{module.title}</h2>
                        <p className="text-slate-500 mb-6 leading-relaxed">
                            {module.description}
                        </p>
                        <div className="space-y-3">
                            {module.lessons.map(lesson => (
                                <div key={lesson.id} className="flex items-center space-x-3 text-slate-600">
                                    <div className="w-2 h-2 rounded-full bg-slate-300" />
                                    <span>{lesson.title}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
