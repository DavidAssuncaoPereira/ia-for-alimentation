import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, Alert } from 'react-native';
import { useNavigation, useRoute } from '@react-navigation/native';
import { AnalysisResponse, AnalyzedFoodItem, recalculateMeal } from '../api/client';
import { useMealStore } from '../store/useMealStore';
import SegmentationView from '../components/SegmentationView';
import VoiceAdjustment from '../components/VoiceAdjustment';
import { Check } from 'lucide-react-native';

export default function AnalysisResultScreen() {
  const navigation = useNavigation<any>();
  const route = useRoute<any>();

  const { imageUri, analysisResult } = route.params as { imageUri: string, analysisResult: AnalysisResponse };

  const addMeal = useMealStore(state => state.addMeal);

  const [items, setItems] = useState<AnalyzedFoodItem[]>(analysisResult.items);
  const [totals, setTotals] = useState(analysisResult.totals);
  const [selectedIndex, setSelectedIndex] = useState<number | undefined>(undefined);

  const handleSave = () => {
    addMeal({
      id: Date.now().toString(),
      timestamp: Date.now(),
      imageUri,
      items,
      totals
    });
    navigation.popToTop();
  };

  const handleAdjustWeight = (index: number, delta: number) => {
    // In a real app, we'd use a slider. For simplicity, we use buttons here that call recalculate
    const newItems = [...items];
    const targetItem = newItems[index];

    if (targetItem.weight_g + delta <= 0) return;

    // Optimistically update weight
    targetItem.weight_g += delta;

    // Call backend to recalculate macros properly
    triggerRecalculate(newItems);
  };

  const triggerRecalculate = async (currentItems: AnalyzedFoodItem[]) => {
    try {
      const requestPayload = currentItems.map(item => ({
        food_slug: item.food_slug,
        weight_g: item.weight_g,
        added_kcal: 0, // Simplified for this function
        added_fat: 0
      }));

      const newResult = await recalculateMeal(requestPayload);

      // Merge results keeping polygons
      const merged = currentItems.map((item, idx) => ({
        ...item,
        volume_cm3: newResult.items[idx].volume_cm3,
        macros: newResult.items[idx].macros
      }));

      setItems(merged);
      setTotals(newResult.totals);
    } catch (e) {
      console.error(e);
      Alert.alert("Error", "Failed to recalculate.");
    }
  };

  const handleAddOil = async () => {
    if (selectedIndex === undefined) {
      Alert.alert("Select Item", "Tap on a food item in the image first to add oil/butter.");
      return;
    }

    const newItems = [...items];
    const target = newItems[selectedIndex];

    try {
      const requestPayload = newItems.map((item, idx) => ({
        food_slug: item.food_slug,
        weight_g: item.weight_g,
        added_kcal: idx === selectedIndex ? 90 : 0,
        added_fat: idx === selectedIndex ? 10 : 0
      }));

      const newResult = await recalculateMeal(requestPayload);

      const merged = newItems.map((item, idx) => ({
        ...item,
        macros: newResult.items[idx].macros
      }));

      setItems(merged);
      setTotals(newResult.totals);
    } catch (e) {
      console.error(e);
    }
  };

  const handleAddFrying = async () => {
    if (selectedIndex === undefined) {
      Alert.alert("Select Item", "Tap on a food item in the image first.");
      return;
    }
    // Conceptually similar to add oil, but with different modifiers
    const newItems = [...items];

    try {
      const requestPayload = newItems.map((item, idx) => ({
        food_slug: item.food_slug,
        weight_g: item.weight_g,
        added_kcal: idx === selectedIndex ? 120 : 0,
        added_fat: idx === selectedIndex ? 13 : 0
      }));

      const newResult = await recalculateMeal(requestPayload);

      const merged = newItems.map((item, idx) => ({
        ...item,
        macros: newResult.items[idx].macros
      }));

      setItems(merged);
      setTotals(newResult.totals);
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <View style={styles.container}>
      <SegmentationView
        imageUri={imageUri}
        items={items}
        selectedItemIndex={selectedIndex}
        onSelect={setSelectedIndex}
      />

      <View style={styles.sheet}>
        <View style={styles.handle} />

        <View style={styles.totalsHeader}>
          <Text style={styles.totalKcal}>{Math.round(totals.kcal)} kcal</Text>
          <Text style={styles.totalMacros}>
            P: {Math.round(totals.protein)}g • C: {Math.round(totals.carbs)}g • F: {Math.round(totals.fat)}g
          </Text>
        </View>

        <ScrollView style={styles.itemList}>
          <VoiceAdjustment onAddOil={handleAddOil} onAddFrying={handleAddFrying} />

          {items.map((item, index) => (
            <TouchableOpacity
              key={index}
              style={[styles.itemCard, selectedIndex === index && styles.itemCardSelected]}
              onPress={() => setSelectedIndex(index)}
            >
              <View style={styles.itemHeader}>
                <Text style={styles.itemName}>{item.food_name}</Text>
                <Text style={styles.itemKcal}>{Math.round(item.macros.kcal)} kcal</Text>
              </View>

              <Text style={styles.itemDetails}>
                Est. Vol: {item.volume_cm3} cm³ • Wt: {item.weight_g} g
              </Text>

              {selectedIndex === index && (
                <View style={styles.adjustmentRow}>
                  <TouchableOpacity style={styles.adjBtn} onPress={() => handleAdjustWeight(index, -10)}>
                    <Text style={styles.adjBtnText}>-10g</Text>
                  </TouchableOpacity>
                  <Text style={styles.adjValue}>{item.weight_g}g</Text>
                  <TouchableOpacity style={styles.adjBtn} onPress={() => handleAdjustWeight(index, 10)}>
                    <Text style={styles.adjBtnText}>+10g</Text>
                  </TouchableOpacity>
                </View>
              )}
            </TouchableOpacity>
          ))}
        </ScrollView>

        <TouchableOpacity style={styles.saveBtn} onPress={handleSave}>
          <Check color="#fff" size={20} />
          <Text style={styles.saveBtnText}>Log Meal</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000',
  },
  sheet: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    height: '50%',
    backgroundColor: '#1C1C1E',
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    padding: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: -3 },
    shadowOpacity: 0.5,
    shadowRadius: 10,
    elevation: 10,
  },
  handle: {
    width: 40,
    height: 5,
    backgroundColor: '#555',
    borderRadius: 3,
    alignSelf: 'center',
    marginBottom: 10,
  },
  totalsHeader: {
    alignItems: 'center',
    borderBottomWidth: 1,
    borderBottomColor: '#333',
    paddingBottom: 12,
    marginBottom: 12,
  },
  totalKcal: {
    color: '#fff',
    fontSize: 28,
    fontWeight: 'bold',
  },
  totalMacros: {
    color: '#aaa',
    fontSize: 14,
    marginTop: 4,
  },
  itemList: {
    flex: 1,
  },
  itemCard: {
    backgroundColor: '#2C2C2E',
    padding: 12,
    borderRadius: 10,
    marginBottom: 10,
  },
  itemCardSelected: {
    borderColor: '#32ADE6',
    borderWidth: 1,
  },
  itemHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 4,
  },
  itemName: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  itemKcal: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  itemDetails: {
    color: '#888',
    fontSize: 12,
  },
  adjustmentRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 12,
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: '#444',
  },
  adjBtn: {
    backgroundColor: '#444',
    paddingVertical: 6,
    paddingHorizontal: 16,
    borderRadius: 8,
  },
  adjBtnText: {
    color: '#fff',
    fontWeight: 'bold',
  },
  adjValue: {
    color: '#fff',
    fontSize: 18,
    marginHorizontal: 20,
    fontWeight: 'bold',
  },
  saveBtn: {
    flexDirection: 'row',
    backgroundColor: '#32ADE6',
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 10,
  },
  saveBtnText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
    marginLeft: 8,
  }
});
