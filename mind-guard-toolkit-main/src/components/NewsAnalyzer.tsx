import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { AlertTriangle, CheckCircle, Shield, Brain, Plus, Zap } from "lucide-react";
import { AnalysisResult } from "./AnalysisResult";
import { DigitalImmunityTip } from "./DigitalImmunityTip";
import { DarkModeToggle } from "./DarkModeToggle";
import { FileUpload } from "./FileUpload";

interface AnalysisData {
  credibilityScore: number;
  status: 'verified' | 'suspicious' | 'misleading';
  explanation: string;
  redFlags: string[];
  sources: string[];
  immunityTip: {
    title: string;
    description: string;
    pattern: string;
  };
}

export function NewsAnalyzer() {
  const [newsContent, setNewsContent] = useState("");
  const [sourceFile, setSourceFile] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<AnalysisData | null>(null);
  const [activeTab, setActiveTab] = useState<"text" | "file">("text");

  const mockAnalysis = (): AnalysisData => {
    const mockResults = [
      {
        credibilityScore: 85,
        status: 'verified' as const,
        explanation: "This content shows strong journalistic standards with proper attribution, balanced reporting, and verifiable facts. The language is neutral and sources are credible.",
        redFlags: [],
        sources: ["Reuters", "Associated Press", "Government Records"],
        immunityTip: {
          title: "Look for Source Attribution",
          description: "Credible news always cites specific sources and provides context. Notice how this article mentions where information came from.",
          pattern: "Multiple independent sources + specific quotes + official records"
        }
      },
      {
        credibilityScore: 35,
        status: 'suspicious' as const,
        explanation: "This content contains several warning signs of potential misinformation including emotional language, lack of credible sources, and unverified claims.",
        redFlags: [
          "Uses highly emotional language designed to provoke anger",
          "Makes claims without citing credible sources",
          "Contains absolute statements without nuance",
          "Appeals to conspiracy theories"
        ],
        sources: ["Unverified social media posts", "Anonymous sources"],
        immunityTip: {
          title: "Emotional Manipulation Alert",
          description: "Be wary of content that tries to make you angry or scared without providing solid evidence. This often indicates bias or manipulation.",
          pattern: "Strong emotions + weak evidence = Red flag"
        }
      },
      {
        credibilityScore: 15,
        status: 'misleading' as const,
        explanation: "This content shows clear signs of misinformation with false claims, misleading statistics, and deliberate manipulation of facts.",
        redFlags: [
          "Contains factually incorrect information",
          "Misrepresents statistical data",
          "Uses outdated or irrelevant information",
          "Lacks any credible source verification"
        ],
        sources: ["No credible sources found"],
        immunityTip: {
          title: "Fact-Check Before Sharing",
          description: "Always verify claims through multiple independent sources before believing or sharing. This content failed basic fact-checking.",
          pattern: "Unverified claims + missing context = Misinformation"
        }
      }
    ];
    
    return mockResults[Math.floor(Math.random() * mockResults.length)];
  };

  const analyzeNews = async () => {
    if (!newsContent.trim()) return;
    
    setIsAnalyzing(true);
    // Simulate API call delay
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    const result = mockAnalysis();
    setAnalysisResult(result);
    setIsAnalyzing(false);
  };

  const handleFileTextExtracted = (extractedText: string, filename: string) => {
    setNewsContent(extractedText);
    setSourceFile(filename);
    setActiveTab("text"); // Switch to text tab to show extracted content
  };

  return (
    <div className="w-full max-w-4xl mx-auto space-y-8 p-6 relative">
      {/* Dark mode toggle */}
      <div className="absolute top-0 right-0 z-50">
        <DarkModeToggle />
      </div>
      
      {/* Header */}
      <div className="text-center space-y-6 relative">
        <div className="absolute inset-0 bg-gradient-glow opacity-50 blur-3xl -z-10" />
        <div className="flex items-center justify-center gap-4 mb-6">
          <div className="relative">
            <Shield className="h-12 w-12 text-primary animate-float drop-shadow-lg" />
            <div className="absolute inset-0 h-12 w-12 text-primary animate-pulse-slow opacity-30" />
          </div>
          <h1 className="text-5xl font-bold ">
            TrustLens AI
          </h1>
        </div>
        <div className="relative">
         
          <div className="flex items-center justify-center gap-6 mt-6">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <div className="h-2 w-2 bg-verified rounded-full animate-pulse-slow" />
              <span>Real-time Analysis</span>
            </div>
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <div className="h-2 w-2 bg-accent rounded-full animate-pulse-slow" />
              <span>Educational Insights</span>
            </div>
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <div className="h-2 w-2 bg-warning rounded-full animate-pulse-slow" />
              <span>Pattern Recognition</span>
            </div>
          </div>
        </div>
      </div>

      {/* Input Section */}
      <Card className="shadow-colored bg-gradient-card border border-primary/10 hover:border-primary/20 transition-all duration-300">
        <CardContent className="p-4">
          <div className="relative">
            <Textarea
              placeholder="Analyze any news content... (articles, tweets, headlines, social media posts)"
              value={newsContent}
              onChange={(e) => setNewsContent(e.target.value)}
              className="min-h-[120px] pr-12 resize-none text-base leading-relaxed rounded-xl border-2 focus:border-primary/50 transition-all duration-300 focus:ring-0 focus:outline-none"
            />
            <div className="absolute bottom-3 right-3 flex items-center gap-3">
              <Button
                onClick={() => setActiveTab("file")}
                variant="ghost"
                size="icon"
                className="h-8 w-8 rounded-full border-2 border-muted-foreground/20 hover:border-primary/50 hover:bg-accent/10 transition-all duration-300 flex items-center justify-center"
                title="Upload file"
              >
                <input
                  type="file"
                  className="absolute inset-0 w-8 h-8 opacity-0 cursor-pointer"
                  onChange={(e) => {
                    if (e.target.files?.[0]) {
                      setActiveTab("file");
                    }
                  }}
                />
                <Plus className="h-4 w-4 text-muted-foreground hover:text-primary transition-colors" />
              </Button>
              <Button
                onClick={analyzeNews}
                disabled={!newsContent.trim() || isAnalyzing}
                className="bg-gradient-hero hover:shadow-colored transition-all duration-300 text-white rounded-lg h-8 px-4 min-w-[120px]"
              >
                {isAnalyzing ? (
                  <Zap className="h-4 w-4 animate-bounce" />
                ) : (
                  <>
                    <Brain className="h-4 w-4 mr-2" />
                    <span>Analyze</span>
                  </>
                )}
              </Button>
            </div>
          </div>

          {/* Analysis Progress */}
          {isAnalyzing && (
            <div className="mt-4 space-y-2 animate-fadeIn">
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <div className="h-2 w-2 bg-primary rounded-full animate-pulse" />
                <span>AI is analyzing the content...</span>
              </div>
              <div className="w-full bg-muted/30 rounded-full h-1 overflow-hidden">
                <div className="h-full bg-gradient-hero animate-pulse rounded-full" 
                     style={{ width: '100%', animationDuration: '2s' }} />
              </div>
            </div>
          )}

          {/* Content Stats */}
          {newsContent && !isAnalyzing && (
            <div className="mt-2 flex items-center gap-4 text-xs text-muted-foreground">
              <span>{newsContent.split(' ').length} words</span>
              <span>•</span>
              <span>{newsContent.length} characters</span>
              {sourceFile && (
                <>
                  <span>•</span>
                  <span className="text-primary">From: {sourceFile}</span>
                </>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Results Section */}
      {analysisResult && (
        <div className="space-y-8 animate-slideUp">
          <AnalysisResult data={analysisResult} />
          <DigitalImmunityTip tip={analysisResult.immunityTip} />
        </div>
      )}

      {/* Quick Tips */}
      {!analysisResult && (
        <Card className="shadow-medium border-accent/20 hover:shadow-glow transition-all duration-300">
          <CardHeader className="pb-4">
            <CardTitle className="text-xl flex items-center gap-3">
              <div className="p-2 bg-gradient-trust rounded-lg shadow-medium">
                <Shield className="h-5 w-5 text-white" />
              </div>
              <span className="bg-gradient-trust bg-clip-text text-transparent">Quick Digital Immunity Tips</span>
            </CardTitle>
            <CardDescription>
              Start building your resistance to misinformation with these essential techniques
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-3 gap-6">
              <div className="group p-4 rounded-lg border border-verified/20 hover:border-verified/40 transition-all duration-300 hover:shadow-medium bg-gradient-to-br from-verified/5 to-transparent">
                <div className="flex items-start gap-3">
                  <div className="p-2 bg-verified/10 rounded-lg group-hover:bg-verified/20 transition-colors">
                    <CheckCircle className="h-5 w-5 text-verified" />
                  </div>
                  <div className="space-y-2">
                    <h4 className="font-semibold text-verified">Check Sources</h4>
                    <p className="text-sm text-muted-foreground leading-relaxed">Look for credible, named sources and official documentation</p>
                  </div>
                </div>
              </div>
              
              <div className="group p-4 rounded-lg border border-warning/20 hover:border-warning/40 transition-all duration-300 hover:shadow-medium bg-gradient-to-br from-warning/5 to-transparent">
                <div className="flex items-start gap-3">
                  <div className="p-2 bg-warning/10 rounded-lg group-hover:bg-warning/20 transition-colors">
                    <AlertTriangle className="h-5 w-5 text-warning" />
                  </div>
                  <div className="space-y-2">
                    <h4 className="font-semibold text-warning">Emotional Language</h4>
                    <p className="text-sm text-muted-foreground leading-relaxed">Be wary of content designed to make you angry or scared</p>
                  </div>
                </div>
              </div>
              
              <div className="group p-4 rounded-lg border border-accent/20 hover:border-accent/40 transition-all duration-300 hover:shadow-medium bg-gradient-to-br from-accent/5 to-transparent">
                <div className="flex items-start gap-3">
                  <div className="p-2 bg-accent/10 rounded-lg group-hover:bg-accent/20 transition-colors">
                    <Shield className="h-5 w-5 text-accent" />
                  </div>
                  <div className="space-y-2">
                    <h4 className="font-semibold text-accent">Cross-Reference</h4>
                    <p className="text-sm text-muted-foreground leading-relaxed">Verify claims through multiple independent sources</p>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="mt-6 p-4 bg-gradient-glow rounded-lg border border-primary/10">
              <div className="flex items-center gap-3 mb-2">
                <Brain className="h-5 w-5 text-primary animate-pulse-slow" />
                <span className="font-medium text-primary">Pro Tip</span>
              </div>
              <p className="text-sm text-muted-foreground">
                The more you practice these techniques, the stronger your digital immunity becomes. Start with one piece of content at a time!
              </p>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}