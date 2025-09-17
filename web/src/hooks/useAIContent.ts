import { useState, useCallback } from 'react';
import { apiService } from '@/lib/api';

export interface AIContentRequest {
  prompt: string;
  type: 'caption' | 'post' | 'idea' | 'hashtags' | 'alt_text';
  context?: string;
  brand_voice?: string;
  platform?: string;
}

export interface AIContentResponse {
  content: string;
  suggestions?: string[];
  metadata?: {
    word_count: number;
    character_count: number;
    estimated_engagement: number;
  };
}

export interface AIContentState {
  loading: boolean;
  error: string | null;
  result: AIContentResponse | null;
  isGenerating: boolean;
}

export function useAIContent() {
  const [state, setState] = useState<AIContentState>({
    loading: false,
    error: null,
    result: null,
    isGenerating: false,
  });

  const generateContent = useCallback(async (request: AIContentRequest) => {
    setState(prev => ({
      ...prev,
      loading: true,
      isGenerating: true,
      error: null,
      result: null,
    }));

    try {
      const response = await apiService.generateContent(request.prompt, request.type);
      
      setState(prev => ({
        ...prev,
        loading: false,
        isGenerating: false,
        result: response.data,
      }));

      return response.data;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to generate content';
      
      setState(prev => ({
        ...prev,
        loading: false,
        isGenerating: false,
        error: errorMessage,
      }));

      throw error;
    }
  }, []);

  const validateContent = useCallback(async (content: string) => {
    setState(prev => ({ ...prev, loading: true, error: null }));

    try {
      const response = await apiService.validateContent(content);
      
      setState(prev => ({
        ...prev,
        loading: false,
        result: {
          content,
          suggestions: response.data.suggestions,
        },
      }));

      return response.data;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to validate content';
      
      setState(prev => ({
        ...prev,
        loading: false,
        error: errorMessage,
      }));

      throw error;
    }
  }, []);

  const clearResult = useCallback(() => {
    setState({
      loading: false,
      error: null,
      result: null,
      isGenerating: false,
    });
  }, []);

  return {
    ...state,
    generateContent,
    validateContent,
    clearResult,
  };
}

// Specialized hooks for different content types
export function useCaptionGenerator() {
  const aiContent = useAIContent();

  const generateCaption = useCallback(async (
    brief: string,
    brandVoice?: string,
    platform?: string
  ) => {
    return aiContent.generateContent({
      prompt: brief,
      type: 'caption',
      brand_voice: brandVoice,
      platform,
    });
  }, [aiContent.generateContent]);

  return {
    ...aiContent,
    generateCaption,
  };
}

export function usePostIdeas() {
  const aiContent = useAIContent();

  const generateIdeas = useCallback(async (
    topic: string,
    platform?: string,
    count: number = 5
  ) => {
    return aiContent.generateContent({
      prompt: `Generate ${count} creative post ideas about: ${topic}`,
      type: 'idea',
      platform,
    });
  }, [aiContent.generateContent]);

  return {
    ...aiContent,
    generateIdeas,
  };
}

export function useHashtagGenerator() {
  const aiContent = useAIContent();

  const generateHashtags = useCallback(async (
    content: string,
    platform?: string,
    count: number = 10
  ) => {
    return aiContent.generateContent({
      prompt: `Generate ${count} relevant hashtags for this content: ${content}`,
      type: 'hashtags',
      platform,
    });
  }, [aiContent.generateContent]);

  return {
    ...aiContent,
    generateHashtags,
  };
}
