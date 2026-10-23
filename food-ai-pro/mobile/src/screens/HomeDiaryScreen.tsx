import React from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, Image } from 'react-native';
import { useMealStore } from '../store/useMealStore';
import MacroRingChart from '../components/MacroRingChart';
import { Plus, Settings } from 'lucide-react-native';

export default function HomeDiaryScreen({ navigation }: any) {
  const meals = useMealStore((state) => state.meals);
  const dailyTargets = useMealStore((state) => state.dailyTargets);
  const getTodayTotals = useMealStore((state) => state.getTodayTotals);

  const totals = getTodayTotals();

  // Simple chronological filter for today
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const todaysMeals = meals.filter(m => new Date(m.timestamp) >= today).reverse();

  return (
    <View style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.headerRow}>
          <Text style={styles.dateText}>{new Date().toDateString()}</Text>
          <TouchableOpacity onPress={() => navigation.navigate('Calibration')}>
            <Settings color="#fff" size={24} />
          </TouchableOpacity>
        </View>

        <View style={styles.ringContainer}>
          <MacroRingChart
            kcal={totals.kcal} kcalTarget={dailyTargets.kcal}
            protein={totals.protein} proteinTarget={dailyTargets.protein}
            carbs={totals.carbs} carbsTarget={dailyTargets.carbs}
            fat={totals.fat} fatTarget={dailyTargets.fat}
          />
          <View style={styles.macroLabels}>
            <View style={styles.macroLabel}>
              <View style={[styles.dot, { backgroundColor: '#32ADE6' }]} />
              <Text style={styles.labelText}>Protein {Math.round(totals.protein)}g / {dailyTargets.protein}g</Text>
            </View>
            <View style={styles.macroLabel}>
              <View style={[styles.dot, { backgroundColor: '#FF9500' }]} />
              <Text style={styles.labelText}>Carbs {Math.round(totals.carbs)}g / {dailyTargets.carbs}g</Text>
            </View>
            <View style={styles.macroLabel}>
              <View style={[styles.dot, { backgroundColor: '#FF2D55' }]} />
              <Text style={styles.labelText}>Fat {Math.round(totals.fat)}g / {dailyTargets.fat}g</Text>
            </View>
          </View>
        </View>

        <Text style={styles.sectionTitle}>Today's Meals</Text>

        {todaysMeals.length === 0 ? (
          <Text style={styles.emptyText}>No meals logged today yet.</Text>
        ) : (
          todaysMeals.map((meal) => (
            <View key={meal.id} style={styles.mealCard}>
              {meal.imageUri && (
                <Image source={{ uri: meal.imageUri }} style={styles.mealImage} />
              )}
              <View style={styles.mealInfo}>
                <Text style={styles.mealTime}>
                  {new Date(meal.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </Text>
                <Text style={styles.mealKcal}>{Math.round(meal.totals.kcal)} kcal</Text>
                <Text style={styles.mealMacros}>
                  P: {Math.round(meal.totals.protein)}g • C: {Math.round(meal.totals.carbs)}g • F: {Math.round(meal.totals.fat)}g
                </Text>
                <Text style={styles.mealItems} numberOfLines={1}>
                  {meal.items.map(i => i.food_name).join(', ')}
                </Text>
              </View>
            </View>
          ))
        )}
      </ScrollView>

      <TouchableOpacity
        style={styles.fab}
        onPress={() => navigation.navigate('Scanner')}
      >
        <Plus color="#fff" size={32} />
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#121212',
  },
  scrollContent: {
    padding: 16,
    paddingBottom: 100, // Space for FAB
  },
  headerRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 20,
  },
  dateText: {
    color: '#fff',
    fontSize: 20,
    fontWeight: 'bold',
  },
  ringContainer: {
    alignItems: 'center',
    marginBottom: 30,
  },
  macroLabels: {
    marginTop: 20,
    width: '100%',
    paddingHorizontal: 20,
  },
  macroLabel: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  dot: {
    width: 10,
    height: 10,
    borderRadius: 5,
    marginRight: 10,
  },
  labelText: {
    color: '#ccc',
    fontSize: 14,
  },
  sectionTitle: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 15,
  },
  emptyText: {
    color: '#888',
    fontStyle: 'italic',
    textAlign: 'center',
    marginTop: 20,
  },
  mealCard: {
    backgroundColor: '#1E1E1E',
    borderRadius: 12,
    flexDirection: 'row',
    padding: 12,
    marginBottom: 12,
  },
  mealImage: {
    width: 60,
    height: 60,
    borderRadius: 8,
    marginRight: 12,
  },
  mealInfo: {
    flex: 1,
    justifyContent: 'center',
  },
  mealTime: {
    color: '#888',
    fontSize: 12,
  },
  mealKcal: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
    marginVertical: 2,
  },
  mealMacros: {
    color: '#ccc',
    fontSize: 12,
  },
  mealItems: {
    color: '#888',
    fontSize: 12,
    marginTop: 4,
  },
  fab: {
    position: 'absolute',
    right: 20,
    bottom: 30,
    backgroundColor: '#32ADE6',
    width: 64,
    height: 64,
    borderRadius: 32,
    alignItems: 'center',
    justifyContent: 'center',
    elevation: 8,
    shadowColor: '#000',
    shadowOpacity: 0.3,
    shadowOffset: { width: 0, height: 4 },
    shadowRadius: 5,
  }
});
