import React from 'react';
import { NavigationContainer, DarkTheme } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { StatusBar } from 'expo-status-bar';

// Placeholder imports for screens that will be created soon
import HomeDiaryScreen from './screens/HomeDiaryScreen';
import ScannerScreen from './screens/ScannerScreen';
import AnalysisResultScreen from './screens/AnalysisResultScreen';
import CalibrationScreen from './screens/CalibrationScreen';

const Stack = createNativeStackNavigator();

export default function App() {
  return (
    <NavigationContainer theme={DarkTheme}>
      <StatusBar style="light" />
      <Stack.Navigator
        initialRouteName="Home"
        screenOptions={{
          headerStyle: { backgroundColor: '#121212' },
          headerTintColor: '#ffffff',
          headerTitleStyle: { fontWeight: 'bold' },
          contentStyle: { backgroundColor: '#121212' }
        }}
      >
        <Stack.Screen
          name="Home"
          component={HomeDiaryScreen}
          options={{ title: 'Daily Diary' }}
        />
        <Stack.Screen
          name="Scanner"
          component={ScannerScreen}
          options={{ headerShown: false }}
        />
        <Stack.Screen
          name="AnalysisResult"
          component={AnalysisResultScreen}
          options={{ title: 'Meal Analysis' }}
        />
        <Stack.Screen
          name="Calibration"
          component={CalibrationScreen}
          options={{ title: 'Plate Calibration' }}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
