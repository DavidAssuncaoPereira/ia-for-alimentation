import React, { useState } from 'react';
import { View, Text, StyleSheet, TextInput, TouchableOpacity, Alert } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { useMealStore } from '../store/useMealStore';

export default function CalibrationScreen() {
  const navigation = useNavigation();
  const plateDiameterCm = useMealStore(state => state.plateDiameterCm);
  const setPlateDiameter = useMealStore(state => state.setPlateDiameter);

  const [inputVal, setInputVal] = useState(plateDiameterCm.toString());

  const handleSave = () => {
    const val = parseFloat(inputVal);
    if (isNaN(val) || val < 10 || val > 50) {
      Alert.alert("Invalid Input", "Please enter a valid diameter between 10cm and 50cm.");
      return;
    }
    setPlateDiameter(val);
    Alert.alert("Saved", `Plate diameter set to ${val}cm.`);
    navigation.goBack();
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Plate Calibration</Text>
      <Text style={styles.description}>
        For accurate volume estimation, the AI uses your plate as a physical reference scale.
        Enter the diameter of the plate or bowl you usually use.
      </Text>

      <View style={styles.inputContainer}>
        <TextInput
          style={styles.input}
          keyboardType="numeric"
          value={inputVal}
          onChangeText={setInputVal}
          maxLength={4}
        />
        <Text style={styles.unitText}>cm</Text>
      </View>

      <TouchableOpacity style={styles.saveBtn} onPress={handleSave}>
        <Text style={styles.saveBtnText}>Save Calibration</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#121212',
    padding: 20,
    justifyContent: 'center',
  },
  title: {
    color: '#fff',
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 10,
    textAlign: 'center',
  },
  description: {
    color: '#aaa',
    fontSize: 16,
    textAlign: 'center',
    marginBottom: 40,
    lineHeight: 24,
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 40,
  },
  input: {
    backgroundColor: '#2C2C2E',
    color: '#fff',
    fontSize: 32,
    fontWeight: 'bold',
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 10,
    width: 100,
    textAlign: 'center',
  },
  unitText: {
    color: '#888',
    fontSize: 24,
    marginLeft: 10,
    fontWeight: 'bold',
  },
  saveBtn: {
    backgroundColor: '#32ADE6',
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
  },
  saveBtnText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  }
});
