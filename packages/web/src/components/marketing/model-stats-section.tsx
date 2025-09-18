'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Brain, Sparkles, Zap, Cpu } from 'lucide-react';
import { getModelsStats, type ModelsStats } from '@/lib/models';

export function ModelStatsSection() {
  const [stats, setStats] = useState<ModelsStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const modelsStats = await getModelsStats();
        setStats(modelsStats);
      } catch (error) {
        console.error('Error fetching model stats:', error);
        // Fallback stats
        setStats({
          totalModels: 34,
          providerBreakdown: {
            OpenAI: 12,
            Anthropic: 7,
            Google: 4,
            Grok: 7,
            Groq: 6,
          },
          modelsByProvider: {},
          latestModels: ['gpt-5', 'claude-opus-4-1-20250805', 'gemini-2.5-pro'],
        });
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  if (loading) {
    return (
      <section className="bg-primary/5 py-24 sm:py-32">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
              Building the Future of Development
            </h2>
            <p className="mx-auto mt-6 max-w-2xl text-lg leading-8 text-muted-foreground">
              Join us on our journey to revolutionize how developers build software.
            </p>
          </div>
          <div className="flex justify-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
          </div>
        </div>
      </section>
    );
  }

  return (
    <section className="bg-primary/5 py-24 sm:py-32">
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
            Building the Future of Development
          </h2>
          <p className="mx-auto mt-6 max-w-2xl text-lg leading-8 text-muted-foreground">
            Powered by the latest AI models from leading providers.
          </p>
        </div>
        
        {/* Main stats grid */}
        <dl className="grid grid-cols-1 gap-x-8 gap-y-16 text-center lg:grid-cols-3 mb-16">
          <div className="mx-auto flex max-w-xs flex-col gap-y-4">
            <dt className="text-base leading-7 text-muted-foreground flex items-center justify-center gap-2">
              <Brain className="h-5 w-5" />
              AI Models Supported
            </dt>
            <dd className="order-first text-3xl font-semibold tracking-tight sm:text-5xl text-primary">
              {stats?.totalModels || 34}+
            </dd>
          </div>
          <div className="mx-auto flex max-w-xs flex-col gap-y-4">
            <dt className="text-base leading-7 text-muted-foreground flex items-center justify-center gap-2">
              <Sparkles className="h-5 w-5" />
              Code Generation
            </dt>
            <dd className="order-first text-3xl font-semibold tracking-tight sm:text-5xl text-primary">
              AI-Powered
            </dd>
          </div>
          <div className="mx-auto flex max-w-xs flex-col gap-y-4">
            <dt className="text-base leading-7 text-muted-foreground flex items-center justify-center gap-2">
              <Zap className="h-5 w-5" />
              Development Speed
            </dt>
            <dd className="order-first text-3xl font-semibold tracking-tight sm:text-5xl text-primary">
              10x
            </dd>
          </div>
        </dl>

        {/* Provider breakdown */}
        {stats && (
          <div className="mx-auto max-w-4xl">
            <Card className="neon-card">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-center justify-center">
                  <Cpu className="h-5 w-5 text-primary" />
                  AI Provider Distribution
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
                  {Object.entries(stats.providerBreakdown).map(([provider, count]) => {
                    const percentage = (count / stats.totalModels) * 100;
                    const providerColors = {
                      OpenAI: 'bg-green-500',
                      Anthropic: 'bg-orange-500',
                      Google: 'bg-blue-500',
                      Grok: 'bg-purple-500',
                      Groq: 'bg-yellow-500',
                    };
                    
                    return (
                      <div key={provider} className="space-y-2">
                        <div className="flex items-center justify-between">
                          <span className="text-sm font-medium">{provider}</span>
                          <Badge variant="secondary">{count}</Badge>
                        </div>
                        <Progress 
                          value={percentage} 
                          className="h-2"
                          style={{
                            '--progress-background': providerColors[provider as keyof typeof providerColors] || 'bg-primary'
                          } as React.CSSProperties}
                        />
                        <p className="text-xs text-muted-foreground">{percentage.toFixed(1)}%</p>
                      </div>
                    );
                  })}
                </div>
                
                {/* Latest models showcase */}
                <div className="mt-8 pt-6 border-t border-border">
                  <h4 className="text-sm font-medium text-center mb-4">Latest & Most Capable Models</h4>
                  <div className="flex flex-wrap justify-center gap-2">
                    {stats.latestModels.slice(0, 5).map((model) => (
                      <Badge key={model} variant="outline" className="text-xs neon-badge">
                        {model}
                      </Badge>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </section>
  );
}