import React from 'react';
import { View, StyleSheet, Dimensions, Image } from 'react-native';
import Svg, { Polygon } from 'react-native-svg';
import { AnalyzedFoodItem } from '../api/client';

interface SegmentationViewProps {
  imageUri: string;
  items: AnalyzedFoodItem[];
  selectedItemIndex?: number;
  onSelect?: (index: number) => void;
}

export default function SegmentationView({ imageUri, items, selectedItemIndex, onSelect }: SegmentationViewProps) {
  const { width } = Dimensions.get('window');
  // Assume image has 4:3 aspect ratio typically coming from camera
  const displayHeight = (width * 4) / 3;

  // In a real scenario, we need the original image dimensions to scale polygons properly.
  // For this implementation, we assume the backend masks are scaled to the original image
  // and we scale them down to screen space. (Assuming standard 1080x1440 resolution for calculation,
  // though backend could return relative points. Our backend returns absolute points on original image).

  // Hardcoded assumed dimensions of the camera capture.
  // Ideally, this should be passed back from the backend or image metadata.
  const ORIG_WIDTH = 1080;
  const ORIG_HEIGHT = 1440;

  const scaleX = width / ORIG_WIDTH;
  const scaleY = displayHeight / ORIG_HEIGHT;

  return (
    <View style={[styles.container, { width, height: displayHeight }]}>
      <Image source={{ uri: imageUri }} style={StyleSheet.absoluteFill} resizeMode="contain" />

      <Svg height="100%" width="100%" style={StyleSheet.absoluteFill}>
        {items.map((item, index) => {
          if (!item.polygon_mask || item.polygon_mask.length === 0) return null;

          const isSelected = selectedItemIndex === index;

          // Map points to SVG string string and scale them
          const pointsStr = item.polygon_mask
            .map(p => `${p.x * scaleX},${p.y * scaleY}`)
            .join(' ');

          const fill = isSelected ? 'rgba(50, 173, 230, 0.4)' : 'rgba(255, 255, 255, 0.2)';
          const stroke = isSelected ? '#32ADE6' : '#FFFFFF';

          return (
            <Polygon
              key={index}
              points={pointsStr}
              fill={fill}
              stroke={stroke}
              strokeWidth="2"
              onPress={() => onSelect && onSelect(index)}
            />
          );
        })}
      </Svg>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#000',
    overflow: 'hidden',
  },
});
