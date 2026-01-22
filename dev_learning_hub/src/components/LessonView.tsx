import { useParams, Link } from 'react-router-dom';
import { MODULES } from '../data/lessons';
import { CodeBlock } from './CodeBlock';
import { ArrowRight, CheckCircle2 } from 'lucide-react';
import { JobMonitorDemo } from './JobMonitorDemo';
// Wait, I didn't install this. I'll use simple parsing or just render text for MVP. 
// Actually, for MVP I'll implement a simple text parser or just render raw.
// Or better: I'll parse the simple markdown I wrote manually.

// Simple parser for MVP to avoid extra heavy dependencies if I forgot them.
// But I installed @tailwindcss/typography so standard HTML tags will look good.
// Let's write a simple renderer for the `content` string.

// ABORT: The simple parser above is bad. 
// I'll implement a slightly better logic: regex to split by code blocks.

export function LessonView() {
    const { lessonId } = useParams();

    // Find lesson
    let foundLesson = null;
    let nextLesson = null;

    // Flatten search
    const allLessons = MODULES.flatMap(m => m.lessons);
    const currentIndex = allLessons.findIndex(l => l.id === lessonId);

    if (currentIndex !== -1) {
        foundLesson = allLessons[currentIndex];
        nextLesson = allLessons[currentIndex + 1];
    }

    if (!foundLesson) {
        return <div className="p-10 text-center">Lesson not found</div>;
    }

    // Split content by code blocks
    const contentParts = foundLesson.content.split('```');

    return (
        <div className="max-w-4xl mx-auto p-8 md:p-12">
            <div className="mb-8">
                <div className="text-sm text-blue-600 font-bold uppercase tracking-wider mb-2">Tutorial</div>
                <h1 className="text-4xl font-extrabold text-slate-900 mb-6">{foundLesson.title}</h1>
            </div>

            <div className="prose prose-slate prose-lg max-w-none">
                {contentParts.map((part, index) => {
                    if (index % 2 === 1) {
                        // Code block
                        // First line is language usually
                        const [lang, ...codeLines] = part.split('\n');
                        return <CodeBlock key={index} language={lang.trim() || 'javascript'} code={codeLines.join('\n')} />;
                    } else {
                        // Text
                        return (
                            <div key={index} dangerouslySetInnerHTML={{
                                // Simple hacky markdown to HTML for headers/lists/images
                                __html: part
                                    .replace(/^# (.*)/gm, '<h1 class="text-3xl font-bold mt-8 mb-4 text-slate-900">$1</h1>')
                                    .replace(/^## (.*)/gm, '<h2 class="text-2xl font-bold mt-6 mb-3 text-slate-800">$1</h2>')
                                    .replace(/!\[(.*?)\]\((.*?)\)/g, '<img src="$2" alt="$1" class="rounded-xl shadow-lg my-6 w-full max-w-2xl mx-auto border border-slate-200" />')
                                    .replace(/^\d\. (.*)/gm, '<li class="list-decimal ml-4 marker:text-blue-500 marker:font-bold mb-2">$1</li>')
                                    .replace(/^- (.*)/gm, '<li class="list-disc ml-4 marker:text-slate-400 mb-2">$1</li>')
                                    .replace(/\*\*(.*?)\*\*/g, '<strong class="font-bold text-slate-900">$1</strong>')
                                    .replace(/`([^`]+)`/g, '<code class="bg-slate-100 text-slate-800 px-1.5 py-0.5 rounded text-sm font-mono">$1</code>')
                                    .replace(/\n/g, '<br/>')
                            }} />
                        );
                    }
                })}
            </div>

            <hr className="my-12 border-slate-200" />

            {/* Demo Injection for Final Project */}
            {foundLesson.id === 'implementation' && (
                <div className="mb-12">
                    <h2 className="text-2xl font-bold text-slate-900 mb-6">實戰演練：監控模擬器</h2>
                    <p className="text-slate-600 mb-4">
                        這是一個模擬的監控環境。試著輸入任何網址並點擊開始，觀察程式如何模擬「送出請求」、「解析資料」以及「觸發通知」的過程。
                    </p>
                    {/* Lazy load to avoid circular dependencies if any, though import is fine */}
                    <JobMonitorDemo />
                </div>
            )}

            {nextLesson ? (
                <Link
                    to={`/lesson/${nextLesson.id}`}
                    className="group block bg-white border border-slate-200 p-8 rounded-2xl hover:border-blue-500 hover:shadow-lg hover:shadow-blue-500/10 transition-all text-right"
                >
                    <span className="text-sm text-slate-500 font-medium">Next Lesson</span>
                    <div className="flex items-center justify-end space-x-3 mt-2">
                        <span className="text-2xl font-bold text-slate-900 group-hover:text-blue-600 transition-colors">
                            {nextLesson.title}
                        </span>
                        <ArrowRight className="w-6 h-6 text-slate-400 group-hover:text-blue-500 group-hover:translate-x-1 transition-all" />
                    </div>
                </Link>
            ) : (
                <div className="bg-green-50 border border-green-200 p-8 rounded-2xl text-center">
                    <CheckCircle2 className="w-12 h-12 text-green-500 mx-auto mb-4" />
                    <h2 className="text-2xl font-bold text-green-800">恭喜！您已完成所有課程</h2>
                    <p className="text-green-600 mt-2">您已經具備開發自動化工具的基礎能力了。</p>
                </div>
            )}
        </div>
    );
}
