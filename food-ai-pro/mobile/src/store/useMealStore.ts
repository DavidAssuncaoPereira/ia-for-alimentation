import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Macros, AnalyzedFoodItem } from '../api/client';

export interface Meal {
  id: string;
  timestamp: number;
  imageUri?: string;
  items: AnalyzedFoodItem[];
  totals: Macros;
}

interface MealStoreState {
  meals: Meal[];
  dailyTargets: Macros;
  plateDiameterCm: number;
  addMeal: (meal: Meal) => void;
  removeMeal: (id: string) => void;
  setDailyTargets: (targets: Macros) => void;
  setPlateDiameter: (diameterCm: number) => void;
  getTodayTotals: () => Macros;
}

export const useMealStore = create<MealStoreState>()(
  persist(
    (set, get) => ({
      meals: [],
      dailyTargets: {
        kcal: 2000,
        protein: 150,
        carbs: 200,
        fat: 65,
      },
      plateDiameterCm: 26.0,

      addMeal: (meal) => set((state) => ({ meals: [...state.meals, meal] })),

      removeMeal: (id) => set((state) => ({ meals: state.meals.filter(m => m.id !== id) })),

      setDailyTargets: (targets) => set({ dailyTargets: targets }),

      setPlateDiameter: (diameterCm) => set({ plateDiameterCm: diameterCm }),

      getTodayTotals: () => {
        const today = new Date();
        today.setHours(0, 0, 0, 0);

        const todayMeals = get().meals.filter(
          (m) => new Date(m.timestamp) >= today
        );

        return todayMeals.reduce(
          (acc, meal) => ({
            kcal: acc.kcal + meal.totals.kcal,
            protein: acc.protein + meal.totals.protein,
            carbs: acc.carbs + meal.totals.carbs,
            fat: acc.fat + meal.totals.fat,
          }),
          { kcal: 0, protein: 0, carbs: 0, fat: 0 }
        );
      },
    }),
    {
      name: 'meal-storage',
      storage: createJSONStorage(() => AsyncStorage),
    }
  )
);
