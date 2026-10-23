import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { Droplet, Flame } from 'lucide-react-native';

interface VoiceAdjustmentProps {
  onAddOil: () => void;
  onAddFrying: () => void;
}

export default function VoiceAdjustment({ onAddOil, onAddFrying }: VoiceAdjustmentProps) {
  // A production-ready quick adjustment UI for hidden fats, overriding the VLM if it missed it.

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Hidden Fats & Adjustments</Text>
      <Text style={styles.subtitle}>Tap to quickly add hidden calories that the camera might miss.</Text>

      <View style={styles.buttonRow}>
        <TouchableOpacity style={styles.button} onPress={onAddOil}>
          <Droplet color="#FFCC00" size={20} />
          <Text style={styles.buttonText}>+1 tbsp Oil/Butter</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.button} onPress={onAddFrying}>
          <Flame color="#FF3B30" size={20} />
          <Text style={styles.buttonText}>It's Fried</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#1E1E1E',
    padding: 16,
    borderRadius: 12,
    marginVertical: 10,
  },
  title: {
    color: '#FFF',
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  subtitle: {
    color: '#AAA',
    fontSize: 12,
    marginBottom: 12,
  },
  buttonRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  button: {
    flex: 1,
    flexDirection: 'row',
    backgroundColor: '#2C2C2E',
    padding: 12,
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
    marginHorizontal: 4,
  },
  buttonText: {
    color: '#FFF',
    marginLeft: 8,
    fontSize: 14,
    fontWeight: '600',
  }
});
