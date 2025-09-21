/**
 * React hooks for TrustNet API
 * Provides easy-to-use hooks for frontend components
 */

import { useState, useCallback } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { api, AnalysisRequest, AnalysisResponse, TrustScore, ManipulationTechnique, getErrorMessage } from '@/lib/api';

// Hook for content analysis
export const useAnalysis = () => {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const queryClient = useQueryClient();

  const analyzeContent = useCallback(async (request: AnalysisRequest): Promise<AnalysisResponse> => {
    setIsAnalyzing(true);
    try {
      const result = await api.analyzeContent(request);
      // Invalidate related queries
      queryClient.invalidateQueries({ queryKey: ['analysis'] });
      return result;
    } finally {
      setIsAnalyzing(false);
    }
  }, [queryClient]);

  const mutation = useMutation({
    mutationFn: analyzeContent,
    onSuccess: (data) => {
      // Cache the result
      queryClient.setQueryData(['analysis', data.analysis_id], data);
    },
  });

  return {
    analyzeContent: mutation.mutate,
    analyzeContentAsync: mutation.mutateAsync,
    isAnalyzing: mutation.isPending || isAnalyzing,
    error: mutation.error,
    data: mutation.data,
    reset: mutation.reset,
  };
};

// Hook for getting analysis by ID
export const useAnalysisById = (analysisId: string | null) => {
  return useQuery({
    queryKey: ['analysis', analysisId],
    queryFn: () => api.getAnalysis(analysisId!),
    enabled: !!analysisId,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

// Hook for manipulation detection
export const useManipulationDetection = () => {
  const mutation = useMutation({
    mutationFn: (content: string) => api.detectManipulation(content),
  });

  return {
    detectManipulation: mutation.mutate,
    detectManipulationAsync: mutation.mutateAsync,
    isDetecting: mutation.isPending,
    error: mutation.error,
    data: mutation.data,
    reset: mutation.reset,
  };
};

// Hook for trust score calculation
export const useTrustScore = () => {
  const mutation = useMutation({
    mutationFn: (content: string) => api.calculateTrustScore(content),
  });

  return {
    calculateTrustScore: mutation.mutate,
    calculateTrustScoreAsync: mutation.mutateAsync,
    isCalculating: mutation.isPending,
    error: mutation.error,
    data: mutation.data,
    reset: mutation.reset,
  };
};

// Hook for educational content
export const useEducationalContent = (language: string = 'en', limit: number = 10) => {
  return useQuery({
    queryKey: ['educational-content', language, limit],
    queryFn: () => api.getEducationalContent(language, limit),
    staleTime: 30 * 60 * 1000, // 30 minutes
  });
};

// Hook for trending topics
export const useTrendingTopics = (timeRange: string = '7d') => {
  return useQuery({
    queryKey: ['trending-topics', timeRange],
    queryFn: () => api.getTrendingTopics(timeRange),
    staleTime: 15 * 60 * 1000, // 15 minutes
  });
};

// Hook for submitting feedback
export const useFeedback = () => {
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: ({ verdictId, feedback }: { verdictId: string; feedback: any }) =>
      api.submitFeedback(verdictId, feedback),
    onSuccess: () => {
      // Invalidate community stats as feedback affects them
      queryClient.invalidateQueries({ queryKey: ['community-stats'] });
    },
  });

  return {
    submitFeedback: mutation.mutate,
    submitFeedbackAsync: mutation.mutateAsync,
    isSubmitting: mutation.isPending,
    error: mutation.error,
    data: mutation.data,
    reset: mutation.reset,
  };
};

// Hook for community statistics
export const useCommunityStats = () => {
  return useQuery({
    queryKey: ['community-stats'],
    queryFn: () => api.getCommunityStats(),
    staleTime: 10 * 60 * 1000, // 10 minutes
    refetchInterval: 5 * 60 * 1000, // Refetch every 5 minutes
  });
};

// Hook for API health check
export const useHealthCheck = () => {
  return useQuery({
    queryKey: ['health'],
    queryFn: () => api.healthCheck(),
    retry: 3,
    retryDelay: 1000,
    staleTime: 30 * 1000, // 30 seconds
  });
};

// Utility hook for handling API errors
export const useApiError = () => {
  const handleError = useCallback((error: any) => {
    const message = getErrorMessage(error);
    console.error('API Error:', message, error);
    return message;
  }, []);

  return { handleError };
};

// Hook for batch operations
export const useBatchAnalysis = () => {
  const [batchResults, setBatchResults] = useState<AnalysisResponse[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [progress, setProgress] = useState(0);

  const processBatch = useCallback(async (requests: AnalysisRequest[]) => {
    setIsProcessing(true);
    setProgress(0);
    setBatchResults([]);

    try {
      const results: AnalysisResponse[] = [];
      
      for (let i = 0; i < requests.length; i++) {
        try {
          const result = await api.analyzeContent(requests[i]);
          results.push(result);
          setBatchResults([...results]);
          setProgress(((i + 1) / requests.length) * 100);
        } catch (error) {
          console.error(`Failed to analyze item ${i + 1}:`, error);
          // Continue with other items even if one fails
        }
      }

      return results;
    } finally {
      setIsProcessing(false);
    }
  }, []);

  return {
    processBatch,
    batchResults,
    isProcessing,
    progress,
    reset: () => {
      setBatchResults([]);
      setProgress(0);
    },
  };
};