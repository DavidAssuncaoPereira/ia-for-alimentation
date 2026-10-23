import React, { useEffect, useRef } from 'react';
import { View, Text, StyleSheet, Animated } from 'react-native';
import Svg, { Circle } from 'react-native-svg';

const AnimatedCircle = Animated.createAnimatedComponent(Circle);

interface MacroRingChartProps {
  kcal: number;
  kcalTarget: number;
  protein: number;
  proteinTarget: number;
  carbs: number;
  carbsTarget: number;
  fat: number;
  fatTarget: number;
  size?: number;
  strokeWidth?: number;
}

export default function MacroRingChart({
  kcal, kcalTarget,
  protein, proteinTarget,
  carbs, carbsTarget,
  fat, fatTarget,
  size = 180,
  strokeWidth = 15
}: MacroRingChartProps) {

  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;

  const animateFill = (val: number, target: number, animObj: Animated.Value) => {
    const percentage = Math.min(val / Math.max(target, 1), 1);
    Animated.timing(animObj, {
      toValue: percentage,
      duration: 1000,
      useNativeDriver: true,
    }).start();
  };

  const animProtein = useRef(new Animated.Value(0)).current;
  const animCarbs = useRef(new Animated.Value(0)).current;
  const animFat = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    animateFill(protein, proteinTarget, animProtein);
    animateFill(carbs, carbsTarget, animCarbs);
    animateFill(fat, fatTarget, animFat);
  }, [protein, carbs, fat]);

  const renderRing = (animValue: Animated.Value, color: string, rOff: number) => {
    const r = radius - rOff;
    const circ = r * 2 * Math.PI;
    const strokeDashoffset = animValue.interpolate({
      inputRange: [0, 1],
      outputRange: [circ, 0]
    });

    return (
      <React.Fragment>
        <Circle cx={size/2} cy={size/2} r={r} stroke={color} strokeWidth={strokeWidth} strokeOpacity={0.2} fill="transparent" />
        <AnimatedCircle
          cx={size/2}
          cy={size/2}
          r={r}
          stroke={color}
          strokeWidth={strokeWidth}
          strokeDasharray={`${circ} ${circ}`}
          strokeDashoffset={strokeDashoffset}
          strokeLinecap="round"
          fill="transparent"
          rotation="-90"
          originX={size/2}
          originY={size/2}
        />
      </React.Fragment>
    );
  };

  const gap = strokeWidth + 2;

  return (
    <View style={{ width: size, height: size, alignItems: 'center', justifyContent: 'center' }}>
      <Svg width={size} height={size}>
        {renderRing(animProtein, '#32ADE6', 0)}         {/* Protein - Blue */}
        {renderRing(animCarbs, '#FF9500', gap)}       {/* Carbs - Orange */}
        {renderRing(animFat, '#FF2D55', gap * 2)}     {/* Fat - Red */}
      </Svg>
      <View style={styles.centerText}>
        <Text style={styles.kcalText}>{Math.round(kcal)}</Text>
        <Text style={styles.label}>/ {kcalTarget} kcal</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  centerText: {
    position: 'absolute',
    alignItems: 'center',
    justifyContent: 'center',
  },
  kcalText: {
    color: '#fff',
    fontSize: 24,
    fontWeight: 'bold',
  },
  label: {
    color: '#888',
    fontSize: 12,
  },
});
