import axios from 'axios';
import { Platform } from 'react-native';

// Use 10.0.2.2 for Android emulator to reach localhost, otherwise localhost or local IP
const LOCAL_HOST = Platform.OS === 'android' ? '10.0.2.2' : '127.0.0.1';

export const apiClient = axios.create({
  baseURL: `http://${LOCAL_HOST}:8000/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds for heavy ML processing
});

export interface Macros {
  kcal: number;
  protein: number;
  carbs: number;
  fat: number;
}

export interface AnalyzedFoodItem {
  box: number[];
  polygon_mask: { x: number, y: number }[];
  food_name: string;
  food_slug: string;
  volume_cm3: number;
  weight_g: number;
  macros: Macros;
}

export interface AnalysisResponse {
  items: AnalyzedFoodItem[];
  totals: Macros;
}

// Helper methods for specific endpoints
export const analyzeMeal = async (imageUri: string, plateDiameterCm: number, userNotes?: string): Promise<AnalysisResponse> => {
  const formData = new FormData();

  // React Native fetch/axios formData requires a specific object structure for files
  const filename = imageUri.split('/').pop() || 'photo.jpg';
  const match = /\.(\w+)$/.exec(filename);
  const type = match ? `image/${match[1]}` : `image/jpeg`;

  formData.append('image', {
    uri: imageUri,
    name: filename,
    type,
  } as any);

  formData.append('plate_diameter_cm', plateDiameterCm.toString());
  if (userNotes) {
    formData.append('user_notes', userNotes);
  }

  const response = await apiClient.post<AnalysisResponse>('/analyze-meal', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
};

export const recalculateMeal = async (
  items: { food_slug: string; weight_g: number; added_kcal: number; added_fat: number }[]
): Promise<AnalysisResponse> => {
  const response = await apiClient.post<AnalysisResponse>('/recalculate', { items });
  return response.data;
};
