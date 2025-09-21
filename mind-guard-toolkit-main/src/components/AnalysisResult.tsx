import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { AlertTriangle, CheckCircle, XCircle, Shield, ExternalLink } from "lucide-react";

interface AnalysisData {
  credibilityScore: number;
  status: 'verified' | 'suspicious' | 'misleading';
  explanation: string;
  redFlags: string[];
  sources: string[];
}

interface AnalysisResultProps {
  data: AnalysisData;
}

export function AnalysisResult({ data }: AnalysisResultProps) {
  const getStatusIcon = () => {
    switch (data.status) {
      case 'verified':
        return <CheckCircle className="h-5 w-5 text-verified" />;
      case 'suspicious':
        return <AlertTriangle className="h-5 w-5 text-warning" />;
      case 'misleading':
        return <XCircle className="h-5 w-5 text-destructive" />;
    }
  };

  const getStatusBadge = () => {
    switch (data.status) {
      case 'verified':
        return <Badge className="bg-verified text-verified-foreground">Verified Content</Badge>;
      case 'suspicious':
        return <Badge className="bg-warning text-warning-foreground">Suspicious Content</Badge>;
      case 'misleading':
        return <Badge className="bg-destructive text-destructive-foreground">Misleading Content</Badge>;
    }
  };

  const getScoreColor = () => {
    if (data.credibilityScore >= 70) return "text-verified";
    if (data.credibilityScore >= 40) return "text-warning";
    return "text-destructive";
  };

  const getProgressColor = () => {
    if (data.credibilityScore >= 70) return "bg-verified";
    if (data.credibilityScore >= 40) return "bg-warning";
    return "bg-destructive";
  };

  const getGradientBg = () => {
    switch (data.status) {
      case 'verified':
        return 'bg-gradient-success';
      case 'suspicious':
        return 'bg-gradient-warning';
      case 'misleading':
        return 'bg-gradient-danger';
    }
  };

  return (
    <Card className="shadow-colored border-2 border-primary/10 hover:shadow-glow transition-all duration-300 overflow-hidden">
      <div className={`h-1 ${getGradientBg()}`} />
      <CardHeader className="pb-4">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-3 text-xl">
            <div className={`p-2 rounded-lg shadow-medium ${getGradientBg()}`}>
              {getStatusIcon()}
            </div>
            <span className="bg-gradient-hero bg-clip-text text-transparent">Analysis Results</span>
          </CardTitle>
          <div className="animate-fadeIn">
            {getStatusBadge()}
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Credibility Score */}
        <div className="space-y-4 p-4 rounded-lg bg-gradient-to-br from-background/50 to-muted/20 border border-border/50">
          <div className="flex items-center justify-between">
            <div className="space-y-1">
              <span className="text-sm font-medium text-muted-foreground">Credibility Score</span>
              <div className="flex items-center gap-2">
                <span className={`text-3xl font-bold ${getScoreColor()} animate-fadeIn`}>
                  {data.credibilityScore}
                </span>
                <span className="text-lg text-muted-foreground">/100</span>
              </div>
            </div>
            <div className={`h-16 w-16 rounded-full flex items-center justify-center shadow-medium ${getGradientBg()}`}>
              <span className="text-lg font-bold text-white">{data.credibilityScore}</span>
            </div>
          </div>
          <div className="space-y-2">
            <Progress 
              value={data.credibilityScore} 
              className="h-4 bg-muted/50"
              style={{
                '--progress-foreground': `hsl(var(--${data.credibilityScore >= 70 ? 'verified' : data.credibilityScore >= 40 ? 'warning' : 'destructive'}))`
              } as React.CSSProperties}
            />
            <div className="flex justify-between text-xs text-muted-foreground">
              <span>Low</span>
              <span>Medium</span>
              <span>High</span>
            </div>
          </div>
        </div>

        {/* Explanation */}
        <div className="space-y-4 p-4 rounded-lg bg-gradient-to-br from-background/50 to-muted/20 border border-border/50">
          <h4 className="font-semibold flex items-center gap-3 text-lg">
            <div className="p-2 bg-gradient-hero rounded-lg shadow-medium">
              <Shield className="h-4 w-4 text-white" />
            </div>
            <span className="bg-gradient-hero bg-clip-text text-transparent">AI Analysis Explanation</span>
          </h4>
          <p className="text-muted-foreground leading-relaxed text-base bg-background/30 p-3 rounded-lg border border-border/30">
            {data.explanation}
          </p>
        </div>

        {/* Red Flags */}
        {data.redFlags.length > 0 && (
          <div className="space-y-4 p-4 rounded-lg bg-gradient-to-br from-destructive/5 to-destructive/10 border border-destructive/20">
            <h4 className="font-semibold text-destructive flex items-center gap-3 text-lg">
              <div className="p-2 bg-gradient-danger rounded-lg shadow-medium">
                <AlertTriangle className="h-4 w-4 text-white" />
              </div>
              <span>Warning Signs Detected</span>
              <Badge variant="destructive" className="ml-auto">{data.redFlags.length}</Badge>
            </h4>
            <ul className="space-y-3">
              {data.redFlags.map((flag, index) => (
                <li key={index} className="flex items-start gap-3 text-sm animate-fadeIn" style={{ animationDelay: `${index * 0.1}s` }}>
                  <div className="h-2 w-2 rounded-full bg-destructive mt-2 flex-shrink-0 animate-pulse" />
                  <span className="text-muted-foreground leading-relaxed bg-background/50 p-2 rounded border border-destructive/10">{flag}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Sources */}
        <div className="space-y-4 p-4 rounded-lg bg-gradient-to-br from-background/50 to-muted/20 border border-border/50">
          <h4 className="font-semibold flex items-center gap-3 text-lg">
            <div className="p-2 bg-gradient-trust rounded-lg shadow-medium">
              <ExternalLink className="h-4 w-4 text-white" />
            </div>
            <span className="bg-gradient-trust bg-clip-text text-transparent">Sources Referenced</span>
            <Badge variant="outline" className="ml-auto">{data.sources.length}</Badge>
          </h4>
          {data.sources.length > 0 ? (
            <div className="flex flex-wrap gap-3">
              {data.sources.map((source, index) => (
                <Badge 
                  key={index} 
                  variant="outline" 
                  className="text-sm px-3 py-1 bg-background/50 hover:bg-background/80 transition-colors animate-fadeIn border-verified/30 text-verified"
                  style={{ animationDelay: `${index * 0.1}s` }}
                >
                  {source}
                </Badge>
              ))}
            </div>
          ) : (
            <div className="p-3 bg-destructive/10 rounded-lg border border-destructive/20">
              <p className="text-sm text-destructive italic flex items-center gap-2">
                <AlertTriangle className="h-4 w-4" />
                No credible sources identified in this content.
              </p>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}