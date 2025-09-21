import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Lightbulb, Target, Brain } from "lucide-react";

interface ImmunityTip {
  title: string;
  description: string;
  pattern: string;
}

interface DigitalImmunityTipProps {
  tip: ImmunityTip;
}

export function DigitalImmunityTip({ tip }: DigitalImmunityTipProps) {
  return (
    <Card className="shadow-glow bg-gradient-trust border-accent/30 hover:shadow-colored transition-all duration-300 overflow-hidden animate-slideUp">
      <div className="h-1 bg-gradient-to-r from-accent via-verified to-accent" />
      <CardHeader className="pb-4">
        <CardTitle className="flex items-center gap-3 text-white text-xl">
          <div className="p-2 bg-white/20 rounded-lg shadow-medium backdrop-blur-sm animate-pulse-slow">
            <Brain className="h-6 w-6" />
          </div>
          <span className="flex-1">Digital Immunity Tip</span>
          <Badge className="bg-white/20 text-white border-white/30 backdrop-blur-sm animate-float">
            Learn & Protect
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6 text-white">
        <div className="space-y-4 p-4 bg-white/10 rounded-lg border border-white/20 backdrop-blur-sm">
          <h4 className="font-semibold flex items-center gap-3 text-lg">
            <div className="p-2 bg-white/20 rounded-lg">
              <Lightbulb className="h-5 w-5" />
            </div>
            {tip.title}
          </h4>
          <p className="text-white/90 leading-relaxed text-base bg-white/5 p-3 rounded-lg border border-white/10">
            {tip.description}
          </p>
        </div>
        
        <div className="p-4 bg-white/15 rounded-lg border border-white/30 backdrop-blur-sm">
          <div className="flex items-center gap-3 mb-3">
            <div className="p-2 bg-white/20 rounded-lg">
              <Target className="h-5 w-5" />
            </div>
            <span className="font-semibold text-lg">Pattern to Remember</span>
          </div>
          <div className="p-3 bg-white/10 rounded-lg border border-white/20">
            <p className="text-sm text-white/95 font-mono leading-relaxed">
              {tip.pattern}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3 p-4 bg-white/10 rounded-lg border border-white/20 backdrop-blur-sm">
          <div className="h-8 w-8 bg-white/20 rounded-full flex items-center justify-center">
            <span className="text-lg">💡</span>
          </div>
          <p className="text-sm text-white/80 italic leading-relaxed">
            The more you practice spotting these patterns, the stronger your digital immunity becomes!
          </p>
        </div>
      </CardContent>
    </Card>
  );
}